#!/usr/bin/env python3
"""Print recent documents from MongoDB collections for verification."""
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

MONGODB_URL=os.getenv('MONGODB_URL','mongodb://localhost:27017')
DB=os.getenv('MONGODB_DB_NAME','email_classifier')
client=MongoClient(MONGODB_URL)
db=client[DB]

print('DB:', MONGODB_URL, DB)

for colname in ('processed_emails','classified_emails'):
    col = db[colname]
    total = col.count_documents({})
    print(f"\nCollection `{colname}`: {total} documents")
    print('Latest 5:')
    for doc in col.find().sort('created_at' if colname=='classified_emails' else 'received_date', -1).limit(5):
        mid = doc.get('email_id') or doc.get('message_id') or doc.get('id') or ''
        subj = doc.get('subject') or doc.get('body_text') or doc.get('subject')
        sender = doc.get('sender') or doc.get('from_email') or doc.get('from')
        conf = doc.get('confidence_score') or doc.get('confidence') or doc.get('confidence_score')
        print(f"- id={mid[:24]:24} | subject={str(subj)[:60]:60} | sender={str(sender)[:40]:40} | conf={conf}")
