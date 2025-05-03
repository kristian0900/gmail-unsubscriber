import os
import base64
import time
import asyncio
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_console()
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_unsubscribe_links(msg_payload):
    links = []
    html = base64.urlsafe_b64decode(msg_payload['body']['data'].encode("UTF-8")).decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and "unsubscribe" in href.lower():
            links.append(href)
    return links

async def run():
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get("messages", [])
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg["id"]).execute()
        payload = msg_data["payload"]
        links = get_unsubscribe_links(payload)
        print(f"Unsubscribe links for message {msg['id']}: {links}")
        time.sleep(1)

def main():
    asyncio.run(run())




