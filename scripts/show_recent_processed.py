#!/usr/bin/env python3
"""Show recent processed emails from MongoDB"""
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

MONGODB_URL=os.getenv('MONGODB_URL','mongodb://localhost:27017')
DB=os.getenv('MONGODB_DB_NAME','email_classifier')
client=MongoClient(MONGODB_URL)
db=client[DB]
col=db.processed_emails

print('Total processed_emails:', col.count_documents({}))
print('\nLatest 10 processed_emails:')
for doc in col.find().sort('received_date', -1).limit(10):
    mid = doc.get('message_id') or doc.get('id') or ''
    subj = doc.get('subject') or doc.get('subject')
    sender = doc.get('from_email') or doc.get('from') or doc.get('sender')
    conf = doc.get('confidence_score')
    print(f"- {mid[:24]:24} | {subj[:60]:60} | {sender} | confidence={conf}")
