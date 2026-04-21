#!/usr/bin/env python3
"""
Setup Gmail Push Notifications via Google Cloud Pub/Sub

This script configures your Gmail account to send push notifications
whenever a new email arrives, using Google Cloud Pub/Sub.
"""

import sys
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import pubsub_v1
from googleapiclient.discovery import build

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

def setup_gmail_watch(credentials_path: str, pubsub_topic: str):
    """
    Setup Gmail to watch inbox and send push notifications
    
    Args:
        credentials_path: Path to Google Cloud service account JSON
        pubsub_topic: Full Pub/Sub topic path (projects/{id}/topics/{name})
    """
    
    print("📧 Gmail Push Notification Setup")
    print("=" * 50)
    
    # Load credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=GMAIL_SCOPES
        )
        print("✓ Loaded service account credentials")
    except Exception as e:
        print(f"✗ Failed to load credentials: {e}")
        sys.exit(1)
    
    # Create Gmail API client
    try:
        gmail_service = build('gmail', 'v1', credentials=credentials)
        print("✓ Connected to Gmail API")
    except Exception as e:
        print(f"✗ Failed to connect to Gmail API: {e}")
        sys.exit(1)
    
    # Setup watch on inbox
    try:
        request_body = {
            'topicName': pubsub_topic,
            'labelIds': ['INBOX']
        }
        
        response = gmail_service.users().watch(userId='me', body=request_body).execute()
        
        print(f"✓ Gmail watch configured")
        print(f"  Topic: {pubsub_topic}")
        print(f"  History ID: {response.get('historyId')}")
        print(f"  Expiration: {response.get('expiration')}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to setup Gmail watch: {e}")
        return False

def verify_pubsub_topic(credentials_path: str, gcp_project_id: str, topic_name: str) -> bool:
    """Verify Pub/Sub topic exists"""
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        publisher = pubsub_v1.PublisherClient(credentials=credentials)
        topic_path = publisher.topic_path(gcp_project_id, topic_name)
        publisher.get_topic(request={"topic": topic_path})
        print(f"✓ Verified Pub/Sub topic: {topic_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to verify Pub/Sub topic: {e}")
        return False

def main():
    """Main setup function"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    credentials_path = os.getenv('GCP_CREDENTIALS_PATH', 
                                 './credentials/service-account-key.json')
    pubsub_topic = os.getenv('GCP_PUBSUB_TOPIC')
    
    if not gcp_project_id or not pubsub_topic:
        print("❌ Missing required environment variables:")
        print("   - GCP_PROJECT_ID")
        print("   - GCP_PUBSUB_TOPIC")
        sys.exit(1)
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("\nSetup Instructions:")
        print("1. Go to Google Cloud Console")
        print("2. Create Service Account with Gmail & Pub/Sub permissions")
        print("3. Download JSON key and save to credentials/ folder")
        sys.exit(1)
    
    print("\n📋 Checking prerequisites...\n")
    
    # Verify topic
    topic_name = pubsub_topic.split('/')[-1]
    if not verify_pubsub_topic(credentials_path, gcp_project_id, topic_name):
        print("\n⚠️  Please create the Pub/Sub topic first:")
        print(f"   python scripts/setup_pubsub.py")
        sys.exit(1)
    
    # Setup Gmail watch
    print("\n⏳ Setting up Gmail push notifications...\n")
    if setup_gmail_watch(credentials_path, pubsub_topic):
        print("\n✅ Successfully configured Gmail push notifications!")
        print("\nNext steps:")
        print("1. Emails will now trigger Pub/Sub messages")
        print("2. Start the FastAPI server: docker-compose up -d")
        print("3. Monitor: docker-compose logs -f api")
    else:
        print("\n❌ Failed to setup Gmail notifications")
        sys.exit(1)

if __name__ == '__main__':
    main()
