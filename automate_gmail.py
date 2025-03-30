import os
import base64
import asyncio
import time
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from playwright.async_api import async_playwright
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Authenticate with Gmail API using OAuth
def authenticate_gmail():
    creds = None
    if os.path.exists('token.pkl'):
        import pickle
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token:
            import pickle
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# Extract unsubscribe links from emails
def extract_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=100).execute()
    messages = results.get('messages', [])
    links = []
    seen = set()

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")

        # Check headers first
        for header in headers:
            if header['name'].lower() == 'list-unsubscribe':
                raw = header['value']
                if '<' in raw and '>' in raw:
                    raw_links = [l.strip('<> ') for l in raw.split(',')]
                    for l in raw_links:
                        if l.lower().startswith("http") and l not in seen:
                            links.append({"link": l, "subject": subject})
                            seen.add(l)

        # Fallback: scan HTML body
        parts = msg_data['payload'].get('parts', [])
        for part in parts:
            if part.get('mimeType') == 'text/html':
                html_data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                soup = BeautifulSoup(html_data, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'unsubscribe' in href.lower() and href not in seen:
                        links.append({"link": href, "subject": subject})
                        seen.add(href)

    return links

# Automatically open each unsubscribe link
async def open_links(links):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for i, item in enumerate(links):
            url = item["link"]
            subject = item["subject"]
            print(f"🔗 Opening ({i+1}/{len(links)}): {url}")
            try:
                await page.goto(url, timeout=15000)
                await asyncio.sleep(3)  # Give it time to register
                content = await page.content()
                if "unsubscribe" in url.lower() and "login" in content.lower():
                    result = "Login Required"
                else:
                    result = "Opened"
                results.append({"url": url, "result": result, "subject": subject})
            except Exception as e:
                print(f"❌ Error opening {url}: {e}")
                results.append({"url": url, "result": f"Error: {str(e)}", "subject": subject})

        await browser.close()
    return results

# Log results to Google Sheets
def log_to_google_sheets(results):
    print("📄 Logging to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Unsubscribe Tracker")
    timestamp = datetime.now().strftime("Run_%Y-%m-%d_%H-%M")
    worksheet = sheet.add_worksheet(title=timestamp, rows="100", cols="3")
    worksheet.append_row(["Unsubscribe Link", "Result", "Email Subject"])
    for item in results:
        worksheet.append_row([item["url"], item["result"], item["subject"]])
    print(f"✅ Data logged to sheet tab: {timestamp}")

# Async runner to link everything
async def run():
    print("📬 Scanning Gmail for unsubscribe links...")
    service = authenticate_gmail()
    links = extract_unsubscribe_links(service)
    if not links:
        print("⚠️ No unsubscribe links found.")
        return
    results = await open_links(links)
    log_to_google_sheets(results)

# 🧠 Main function to call from Flask or CLI
def main():
    asyncio.run(run())

