import os
import time
import json
import asyncio
import base64
import logging
import re

from bs4 import BeautifulSoup
from flask import Flask, request
from googleapiclient.discovery import build
from playwright.async_api import async_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds_json = os.environ['GOOGLE_CREDENTIALS_JSON']
    creds_dict = json.loads(creds_json)

    # Replace escaped newlines with actual newlines for private_key
    creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=SCOPES)
    return build('gmail', 'v1', credentials=credentials)

async def get_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get('messages', [])
    unsubscribe_links = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        raw_msg = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        soup = BeautifulSoup(raw_msg, 'html.parser')

        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href and 'unsubscribe' in href.lower():
                unsubscribe_links.append(href)

    return list(set(unsubscribe_links))

async def click_links(links):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        for link in links:
            try:
                await page.goto(link, timeout=15000)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Failed to visit {link}: {e}")

        await browser.close()

def main():
    asyncio.run(run())

async def run():
    service = authenticate_gmail()
    links = await get_unsubscribe_links(service)
    await click_links(links)

if __name__ == '__main__':
    main()

