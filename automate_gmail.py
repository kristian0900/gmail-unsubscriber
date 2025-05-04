import os
import json
import base64
import asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds_json_base64 = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json_base64:
        raise EnvironmentError("GOOGLE_CREDENTIALS_JSON is not set in environment variables.")

    try:
        creds_json = base64.b64decode(creds_json_base64).decode("utf-8")
        creds_dict = json.loads(creds_json)
    except Exception as e:
        raise ValueError(f"Failed to decode or parse GOOGLE_CREDENTIALS_JSON: {e}")

    credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("gmail", "v1", credentials=credentials)
    return service

async def get_unsubscribe_links(service):
    results = service.users().messages().list(userId='me', q="unsubscribe", maxResults=10).execute()
    messages = results.get('messages', [])

    links = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['List-Unsubscribe']).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'list-unsubscribe':
                links.append(header['value'])
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




