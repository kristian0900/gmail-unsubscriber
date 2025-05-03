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
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds_json = os.environ['GOOGLE_CREDENTIALS_JSON']
    creds_dict = json.loads(creds_json)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes=SCOPES)
    delegated_creds = credentials.create_delegated(creds_dict["client_email"])
    return build('gmail', 'v1', credentials=delegated_creds)

def get_unsubscribe_links(msg_payload):
    html = base64.urlsafe_b64decode(msg_payload['body']['data'].encode("UTF-8")).decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if href and "unsubscribe" in href.lower():
            links.append(href)

    return links

async def run():
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get("messages", [])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_data["payload"]
            links = get_unsubscribe_links(payload)

            for link in links:
                print(f"Unsubscribing from: {link}")
                await page.goto(link)
                await asyncio.sleep(2)

        await browser.close()

def main():
    asyncio.run(run())
