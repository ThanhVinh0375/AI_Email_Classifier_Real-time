#!/usr/bin/env python3
"""Poll Gmail (INBOX + SPAM) and upsert messages into MongoDB.

Usage:
  python scripts/poll_gmail_and_upsert.py --once
  python scripts/poll_gmail_and_upsert.py --interval 30
"""
from __future__ import annotations
import os
import time
import argparse
import pickle
import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import build
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

TOKEN_PATH = os.getenv('GMAIL_TOKEN_PATH', './credentials/token.pickle')
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'email_classifier')


def parse_date_header(date_str: str) -> datetime:
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def extract_body(payload: dict) -> str:
    if not payload:
        return ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
        for part in payload['parts']:
            if 'parts' in part:
                res = extract_body(part)
                if res:
                    return res
        return ''
    else:
        data = payload.get('body', {}).get('data')
        if data:
            return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')
        return ''


def process_message(gmail, db, message_id: str) -> None:
    proc_col = db.processed_emails
    cls_col = db.classified_emails
    try:
        msg = gmail.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = msg.get('payload') or {}
        headers = {h.get('name', '').lower(): h.get('value', '') for h in msg.get('payload', {}).get('headers', [])}
        subject = headers.get('subject', '')
        from_email = headers.get('from', '')
        date_hdr = headers.get('date', '')
        received_at = parse_date_header(date_hdr)
        body = extract_body(payload)

        proc_doc = {
            'message_id': message_id,
            'subject': subject,
            'from_email': from_email,
            'body': body,
            'received_at': received_at,
            'is_spam': ('SPAM' in msg.get('labelIds', []) or 'SPAM' in headers.get('x-gm-labels', ''))
        }
        proc_col.update_one({'message_id': message_id}, {'$set': proc_doc}, upsert=True)

        cls_doc = {
            'email_id': message_id,
            'subject': subject,
            'sender': from_email,
            'body_text': body,
            'is_spam': proc_doc['is_spam'],
            'created_at': received_at,
        }
        cls_col.update_one({'email_id': message_id}, {'$set': cls_doc}, upsert=True)
    except Exception as e:
        print('Error processing message', message_id, e)


def poll_once(args) -> None:
    if not os.path.exists(TOKEN_PATH):
        print('Missing token.pickle — run scripts/setup_gmail_oauth.py to authorize')
        return
    with open(TOKEN_PATH, 'rb') as f:
        creds = pickle.load(f)
    gmail = build('gmail', 'v1', credentials=creds)
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]

    q = args.query or 'in:inbox OR in:spam'
    try:
        resp = gmail.users().messages().list(userId='me', q=q, maxResults=args.max).execute()
        messages = resp.get('messages', [])
    except Exception as e:
        print('Error listing messages:', e)
        messages = []

    print('Found messages:', len(messages))
    for m in messages:
        mid = m.get('id')
        if mid:
            process_message(gmail, db, mid)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=30, help='poll interval seconds')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--max', type=int, default=200)
    parser.add_argument('--query', type=str, default='in:inbox OR in:spam')
    args = parser.parse_args()

    if args.once:
        poll_once(args)
        return

    while True:
        poll_once(args)
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
