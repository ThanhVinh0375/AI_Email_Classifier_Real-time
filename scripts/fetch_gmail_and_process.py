#!/usr/bin/env python3
"""
Fetch recent Gmail messages via OAuth and process them through the existing
Hybrid AI pipeline so results are saved into MongoDB and reflected on the dashboard.

This avoids using Pub/Sub/service-account for local testing.
"""
import os
import pickle
import json
import asyncio
from dotenv import load_dotenv
import sys
import os

# Ensure project root is on sys.path so 'src' package imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Use internal services
from src.services import get_email_processing_service, get_gmail_service, get_mongo_service
from src.services.gmail_service import GmailService
from src.utils import get_logger

logger = get_logger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels'
]


def get_oauth_credentials():
    creds = None
    token_path = './credentials/token.pickle'
    client_secrets = './credentials/client_secret.json'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets):
                logger.error('Missing OAuth client_secret.json in ./credentials')
                return None
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)
    return creds


async def process_messages(gmail_service_client, messages):
    email_service = get_email_processing_service()
    results = []
    for m in messages:
        msg_id = m.get('id')
        try:
            resp = gmail_service_client.users().messages().get(userId='me', id=msg_id, format='full').execute()
            # Format using local GmailService parser
            gmail_parser = GmailService()
            formatted = gmail_parser.format_email_data(resp)

            # process
            processed = await email_service.process_email(formatted)
            results.append((msg_id, processed))
        except Exception as e:
            logger.error(f'Error processing message {msg_id}: {e}')
    return results


def main():
    load_dotenv()
    creds = get_oauth_credentials()
    if creds is None:
        logger.error('OAuth credentials unavailable; aborting')
        return

    gmail = build('gmail', 'v1', credentials=creds)

    # List recent messages in INBOX (change query if needed)
    try:
        list_resp = gmail.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
        messages = list_resp.get('messages', [])
        if not messages:
            logger.info('No recent messages found')
            return

        logger.info(f'Found {len(messages)} messages; processing...')

        # Ensure Mongo connected before processing
        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_mongo_service())

        processed = loop.run_until_complete(process_messages(gmail, messages))

        logger.info(f'Processing complete: {len(processed)} items')
        for mid, res in processed:
            logger.info(f'Processed message {mid} -> {getattr(res, "classification", None)}')

    except Exception as e:
        logger.error(f'Failed to list/process messages: {e}')


if __name__ == '__main__':
    main()
