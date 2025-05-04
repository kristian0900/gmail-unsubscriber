import os
import asyncio
import base64
import re

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# If modifying these SCOPES, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()  # Use run_local_server() if running locally with a browser
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

async def get_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get('messages', [])
    links = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        soup = BeautifulSoup(msg_raw, "html.parser")
        found = soup.find_all('a', href=True)
        for a in found:
            if 'unsubscribe' in a['href'].lower():
                links.append(a['href'])
                break
    return links

async def run():
    service = authenticate_gmail()
    links = await get_unsubscribe_links(service)
    print("Found unsubscribe links:")
    for link in links:
        print(link)

def main():
    asyncio.run(run())

if __name__ == '__main__':
    main()


