#!/usr/bin/env python3
"""
Add Sample Emails to MongoDB for Testing

This script adds sample classified emails to the MongoDB database
so you can test the Streamlit dashboard without setting up Gmail webhooks.
"""

import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "email_classifier")

# Sample emails data
SAMPLE_EMAILS = [
    {
        "email_id": "sample_001",
        "sender": "boss@company.com",
        "subject": "Q1 Budget Review Meeting - Action Required",
        "body_text": "Dear Team, please review the Q1 2026 budget proposal and provide feedback by Friday. The deadline for submission is April 25th.",
        "classification_label": "work",
        "confidence_score": 0.92,
        "summary": "Q1 2026 Budget Review Meeting",
        "sentiment": "neutral",
        "extracted_entities": [
            {"type": "DATE", "text": "April 25th", "confidence": 0.95},
            {"type": "ORG", "text": "Q1", "confidence": 0.88}
        ],
        "created_at": datetime.utcnow() - timedelta(hours=2)
    },
    {
        "email_id": "sample_002",
        "sender": "friend@gmail.com",
        "subject": "Dinner plans this weekend?",
        "body_text": "Hey! How about we grab dinner at that new Italian place on Saturday? Let me know what time works for you.",
        "classification_label": "personal",
        "confidence_score": 0.89,
        "summary": "Weekend dinner invitation",
        "sentiment": "positive",
        "extracted_entities": [
            {"type": "DATE", "text": "Saturday", "confidence": 0.92}
        ],
        "created_at": datetime.utcnow() - timedelta(hours=4)
    },
    {
        "email_id": "sample_003",
        "sender": "newsletter@techcrunch.com",
        "subject": "AI Breakthrough: New Language Model Released",
        "body_text": "TechCrunch Newsletter: OpenAI has just released GPT-5 with unprecedented capabilities in code generation and reasoning.",
        "classification_label": "news",
        "confidence_score": 0.85,
        "summary": "Tech news about AI language model",
        "sentiment": "neutral",
        "extracted_entities": [
            {"type": "ORG", "text": "OpenAI", "confidence": 0.96},
            {"type": "PRODUCT", "text": "GPT-5", "confidence": 0.91}
        ],
        "created_at": datetime.utcnow() - timedelta(hours=6)
    },
    {
        "email_id": "sample_004",
        "sender": "bank@chase.com",
        "subject": "Security Alert: Unusual Login Detected",
        "body_text": "We detected a login from an unrecognized device. If this wasn't you, please secure your account immediately.",
        "classification_label": "important",
        "confidence_score": 0.96,
        "summary": "Bank security alert",
        "sentiment": "negative",
        "extracted_entities": [
            {"type": "ORG", "text": "Chase", "confidence": 0.94}
        ],
        "created_at": datetime.utcnow() - timedelta(hours=8)
    },
    {
        "email_id": "sample_005",
        "sender": "spam@unknown.com",
        "subject": "WIN A FREE IPHONE NOW!!!",
        "body_text": "CONGRATULATIONS! You've been selected to win a brand new iPhone. Click here to claim your prize!",
        "classification_label": "spam",
        "confidence_score": 0.98,
        "summary": "Spam email offering free iPhone",
        "sentiment": "positive",
        "extracted_entities": [
            {"type": "PRODUCT", "text": "iPhone", "confidence": 0.87}
        ],
        "created_at": datetime.utcnow() - timedelta(hours=10)
    }
]

async def add_sample_emails():
    """Add sample emails to MongoDB"""
    print("🔄 Connecting to MongoDB...")

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    collection = db["classified_emails"]

    try:
        # Check if samples already exist
        existing_count = await collection.count_documents({"email_id": {"$regex": "^sample_"}})
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing sample emails. Skipping insertion.")
            return

        # Insert sample emails
        print(f"📧 Adding {len(SAMPLE_EMAILS)} sample emails...")
        result = await collection.insert_many(SAMPLE_EMAILS)

        print(f"✅ Successfully added {len(result.inserted_ids)} sample emails!")
        print("\n📊 Sample data includes:")
        print("   - Work emails (budget reviews, meetings)")
        print("   - Personal emails (dinner plans)")
        print("   - News emails (tech updates)")
        print("   - Important emails (security alerts)")
        print("   - Spam emails (prize scams)")
        print("\n🔄 Refresh your Streamlit dashboard to see the data!")

    except Exception as e:
        print(f"❌ Error adding sample emails: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_emails())