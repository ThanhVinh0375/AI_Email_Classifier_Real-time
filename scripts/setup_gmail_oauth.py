#!/usr/bin/env python3
"""
Gmail OAuth Setup for Email Classification

This script handles OAuth 2.0 authentication for Gmail API access.
Service accounts cannot directly access user Gmail data - OAuth flow is required.
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

def setup_oauth_credentials():
    """Setup OAuth 2.0 credentials for Gmail access"""

    print("🔐 Gmail OAuth Setup")
    print("=" * 50)

    # Check for existing credentials
    creds = None
    token_path = './credentials/token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or don't exist, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need OAuth client ID and secret
            client_secrets_path = './credentials/client_secret.json'

            if not os.path.exists(client_secrets_path):
                print("❌ Missing OAuth client credentials!")
                print("\n📋 SETUP REQUIRED:")
                print("1. Go to Google Cloud Console → APIs & Credentials")
                print("2. Create OAuth 2.0 Client ID (Desktop application)")
                print("3. Download JSON and save as: ./credentials/client_secret.json")
                print("4. Run this script again")
                return False

            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    print("✓ OAuth credentials configured")
    return creds

def setup_gmail_watch_oauth(pubsub_topic: str):
    """Setup Gmail watch using OAuth credentials"""

    creds = setup_oauth_credentials()
    if not creds:
        return False

    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
        print("✓ Connected to Gmail API with OAuth")

        # Setup watch on inbox
        request_body = {
            'topicName': pubsub_topic,
            'labelIds': ['INBOX']
        }

        response = gmail_service.users().watch(userId='me', body=request_body).execute()

        print("✓ Gmail watch configured successfully!")
        print(f"  Topic: {pubsub_topic}")
        print(f"  History ID: {response.get('historyId')}")
        print(f"  Expiration: {response.get('expiration')}")

        return True

    except Exception as e:
        print(f"✗ Failed to setup Gmail watch: {e}")
        return False

def main():
    """Main setup function"""
    from dotenv import load_dotenv
    load_dotenv()

    pubsub_topic = os.getenv('GCP_PUBSUB_TOPIC')

    if not pubsub_topic:
        print("❌ Missing GCP_PUBSUB_TOPIC in .env")
        return

    print("Setting up Gmail notifications with OAuth...")
    if setup_gmail_watch_oauth(pubsub_topic):
        print("\n✅ Gmail notifications configured!")
        print("\n🚀 Next steps:")
        print("1. Start services: docker-compose up -d")
        print("2. Check dashboard: http://localhost:8501")
        print("3. New emails will be classified automatically!")
    else:
        print("\n❌ Setup failed")

if __name__ == "__main__":
    main()