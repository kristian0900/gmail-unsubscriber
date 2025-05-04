import os
import re
import json
import asyncio
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from bs4 import BeautifulSoup
import playwright.async_api as playwright_async

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise EnvironmentError("GOOGLE_CREDENTIALS_JSON is not set in environment variables.")

    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('gmail', 'v1', credentials=credentials)
    return service


async def get_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get('messages', [])
    links = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        msg_str = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        soup = BeautifulSoup(msg_str, "html.parser")
        for a in soup.find_all('a', href=True):
            if 'unsubscribe' in a['href'].lower():
                links.append(a['href'])

    return links


async def click_unsubscribe_links(links):
    async with playwright_async.async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for link in links:
            try:
                await page.goto(link, timeout=15000)
                print(f"Visited: {link}")
            except Exception as e:
                print(f"Failed to visit {link}: {e}")
        await browser.close()


async def run():
    service = authenticate_gmail()
    links = await get_unsubscribe_links(service)
    await click_unsubscribe_links(links)


def main():
    asyncio.run(run())


if __name__ == '__main__':
    main()



