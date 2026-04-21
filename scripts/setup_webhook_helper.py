#!/usr/bin/env python3
"""
Gmail Webhook Setup Helper

This script helps you set up Gmail push notifications step by step.
Run this after completing the Google Cloud Console setup.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file has required values"""
    env_path = Path('.env')
    if not env_path.exists():
        print("ERROR: .env file not found!")
        return False

    required_vars = [
        'GCP_PROJECT_ID',
        'GCP_CREDENTIALS_PATH',
        'GCP_PUBSUB_TOPIC',
        'LLM_API_KEY'
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith(('test-', 'your-')):
            missing.append(var)

    if missing:
        print("ERROR: Missing or placeholder values in .env:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease update .env with real values first!")
        return False

    return True

def check_credentials():
    """Check if service account credentials exist"""
    credentials_path = os.getenv('GCP_CREDENTIALS_PATH', './credentials/service-account-key.json')
    if not Path(credentials_path).exists():
        print(f"ERROR - Credentials file not found: {credentials_path}")
        print("\nPlease download the JSON key from Google Cloud Console")
        print("and save it to the credentials/ folder")
        return False

    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
        if creds.get('type') != 'service_account':
            print("ERROR: Credentials file is not a Google service account key.")
            print("   Please upload a JSON file created from a Service Account key.")
            return False
        project_id = creds.get('project_id')
        if project_id:
            print(f"OK - Found service account credentials for project: {project_id}")
            return True
    except Exception as e:
        print(f"ERROR - Invalid credentials file: {e}")
        return False

def create_pubsub_topic():
    """Create Pub/Sub topic using gcloud"""
    project_id = os.getenv('GCP_PROJECT_ID')
    topic_name = 'gmail-notifications'

    print(f"\nCreating Pub/Sub topic: {topic_name}")
    cmd = f'gcloud pubsub topics create {topic_name} --project={project_id}'

    print(f"Run this command: {cmd}")
    print("Press Enter when done...")

    input()

def create_pubsub_subscription():
    """Create Pub/Sub push subscription"""
    project_id = os.getenv('GCP_PROJECT_ID')
    topic_name = 'gmail-notifications'
    subscription_name = 'gmail-notifications-sub'

    # For local development, we'll use ngrok or similar
    webhook_url = "http://localhost:8000/api/v1/webhook/gmail"  # Will need ngrok for production

    print(f"\nCreating Pub/Sub subscription: {subscription_name}")
    cmd = f'''gcloud pubsub subscriptions create {subscription_name} \
  --topic={topic_name} \
  --push-endpoint={webhook_url} \
  --project={project_id}'''

    print(f"Run this command: {cmd}")
    print("NOTE: For production, replace localhost with your actual domain")
    print("Press Enter when done...")

    input()

def setup_gmail_watch():
    """Run the Gmail watch setup script"""
    print("\nSetting up Gmail push notifications...")
    os.system('python scripts/setup_gmail_watch.py')

def main():
    """Main setup function"""
    print("Gmail Webhook Setup Helper")
    print("=" * 50)

    # Load environment variables from .env
    load_dotenv()

    # Check prerequisites
    if not check_env_file():
        return

    if not check_credentials():
        return

    print("\nPrerequisites check passed!")

    # Create Pub/Sub resources
    create_pubsub_topic()
    create_pubsub_subscription()

    # Setup Gmail watch
    setup_gmail_watch()

    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Start the FastAPI server: docker-compose up -d")
    print("2. Send a test email to your Gmail account")
    print("3. Check the dashboard for new emails!")

if __name__ == '__main__':
    main()