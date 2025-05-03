import os
import asyncio
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')

            print("🔐 Visit this URL to authorize the app:\n", auth_url)
            code = input("📥 Enter the authorization code here: ")
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def init_gspread():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('gspread-creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Unsubscribed Emails").sheet1
    return sheet

async def unsubscribe_link_from_body(html_body):
    soup = BeautifulSoup(html_body, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']
        if 'unsubscribe' in href.lower():
            return href

    return None

async def extract_unsubscribe_link(service, message_id):
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = msg['payload']

    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                data = part['body'].get('data')
                if data:
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                    return await unsubscribe_link_from_body(html_body)
    else:
        body = payload.get('body', {}).get('data')
        if body:
            html_body = base64.urlsafe_b64decode(body).decode('utf-8')
            return await unsubscribe_link_from_body(html_body)

    return None

async def click_unsubscribe(link):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(link, timeout=15000)
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error visiting link: {link} — {e}")
        await browser.close()

async def run():
    service = authenticate_gmail()
    sheet = init_gspread()

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='unsubscribe').execute()
    messages = results.get('messages', [])

    processed_senders = set(sheet.col_values(1))

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        sender = next((h['value'] for h in headers if h['name'] == 'From'), None)

        if sender in processed_senders:
            print(f"⏭️ Already unsubscribed from: {sender}")
            continue

        print(f"🔍 Checking: {sender}")
        link = await extract_unsubscribe_link(service, msg['id'])

        if link:
            print(f"🔗 Found link: {link}")
            await click_unsubscribe(link)
            sheet.append_row([sender, link])
        else:
            print(f"❌ No link found for: {sender}")
            sheet.append_row([sender, "No link found"])

def main():
    asyncio.run(run())





