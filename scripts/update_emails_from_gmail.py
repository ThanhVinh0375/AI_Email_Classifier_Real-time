#!/usr/bin/env python3
"""
Fetch each message_id from `processed_emails`, retrieve full message via Gmail API (OAuth token.pickle), parse headers/body, and update `processed_emails` and `classified_emails` documents with real content.
"""
import os
import pickle
from dotenv import load_dotenv
load_dotenv()
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import json
from pymongo import MongoClient

# Load OAuth creds
TOKEN_PATH = './credentials/token.pickle'
if not os.path.exists(TOKEN_PATH):
    print('Missing token.pickle. Run scripts/setup_gmail_oauth.py first to authorize.')
    raise SystemExit(1)

with open(TOKEN_PATH, 'rb') as f:
    creds = pickle.load(f)

gmail = build('gmail', 'v1', credentials=creds)

# Mongo
MONGODB_URL=os.getenv('MONGODB_URL','mongodb://localhost:27017')
DB=os.getenv('MONGODB_DB_NAME','email_classifier')
client=MongoClient(MONGODB_URL)
db=client[DB]
processed_col = db.processed_emails
classified_col = db.classified_emails

count = 0
for doc in processed_col.find():
    mid = doc.get('message_id')
    if not mid:
        continue
    try:
        resp = gmail.users().messages().get(userId='me', id=mid, format='full').execute()
        # parse headers
        headers = {h['name'].lower(): h['value'] for h in resp.get('payload', {}).get('headers', [])}
        subject = headers.get('subject','')
        from_email = headers.get('from','')
        date = headers.get('date')
        # parse body
        def extract_body(payload):
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data','')
                        if data:
                            return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/html':
                        data = part.get('body', {}).get('data','')
                        if data:
                            return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
                return ''
            else:
                data = payload.get('body', {}).get('data','')
                if data:
                    return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
                return ''
        body = extract_body(resp.get('payload', {}))

        # Update processed_emails
        update = {
            'subject': subject,
            'from_email': from_email,
            'body': body,
        }
        processed_col.update_one({'message_id': mid}, {'$set': update})

        # Update classified_emails
        classified_update = {
            'subject': subject,
            'sender': from_email,
            'body_text': body,
            'updated_at': resp.get('internalDate')
        }
        classified_col.update_one({'email_id': mid}, {'$set': classified_update})

        print('Updated', mid, subject[:60])
        count += 1
    except Exception as e:
        print('Error fetching/updating', mid, e)

print('Updated total:', count)
