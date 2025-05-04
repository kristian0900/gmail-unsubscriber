import os
import json
import asyncio
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"

def authenticate_gmail():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

async def get_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get('messages', [])

    unsubscribe_links = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload'].get('headers', [])
        for header in headers:
            if header['name'].lower() == 'list-unsubscribe':
                unsubscribe_links.append(header['value'])
    return unsubscribe_links

def main():
    asyncio.run(run())

async def run():
    service = authenticate_gmail()
    links = await get_unsubscribe_links(service)
    print("Unsubscribe links:", links)

if __name__ == "__main__":
    main()





