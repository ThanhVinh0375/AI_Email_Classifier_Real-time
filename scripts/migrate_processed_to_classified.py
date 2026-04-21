#!/usr/bin/env python3
"""
Migrate documents from `processed_emails` to `classified_emails` so dashboard shows them.
Run: python scripts/migrate_processed_to_classified.py
"""
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os

MONGODB_URL=os.getenv('MONGODB_URL','mongodb://localhost:27017')
DB=os.getenv('MONGODB_DB_NAME','email_classifier')
client=MongoClient(MONGODB_URL)
db=client[DB]
processed_col=db.processed_emails
classified_col=db.classified_emails

count=0
for doc in processed_col.find():
    try:
        email_id = doc.get('message_id') or doc.get('id')
        classified_doc = {
            "email_id": email_id,
            "sender": doc.get('from_email') or doc.get('from'),
            "subject": doc.get('subject'),
            "body_text": doc.get('body', '')[:2000],
            "classification_label": doc.get('classification') if isinstance(doc.get('classification'), str) else getattr(doc.get('classification'), 'value', str(doc.get('classification'))),
            "summary": (doc.get('body','')[:200] if doc.get('body') else ""),
            "extracted_entities": doc.get('extracted_entities', []),
            "sentiment_analysis": doc.get('sentiment_analysis'),
            "processing_time_ms": doc.get('processing_time_ms', 0),
            "model_version": doc.get('model_version', '1.0'),
            "confidence_score": float(doc.get('confidence_score', 0)),
            "created_at": doc.get('processed_at'),
            "updated_at": doc.get('processed_at'),
            "status": doc.get('status','completed'),
            "retry_count": int(doc.get('retry_count',0))
        }
        classified_col.update_one({"email_id": email_id}, {"$set": classified_doc}, upsert=True)
        count += 1
    except Exception as e:
        print('Error migrating doc', doc.get('_id'), e)

print(f'Migrated {count} documents from processed_emails to classified_emails')
