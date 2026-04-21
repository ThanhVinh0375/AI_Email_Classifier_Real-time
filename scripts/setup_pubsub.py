#!/usr/bin/env python3
"""
Setup Google Cloud Application Default Credentials and Pub/Sub resources
"""

import os
import json
from google.oauth2 import service_account
from google.cloud import pubsub_v1
from google.auth.transport.requests import Request

def setup_adc_and_pubsub():
    """Setup ADC and create Pub/Sub resources"""

    # Load environment variables
    credentials_path = os.getenv('GCP_CREDENTIALS_PATH', './credentials/service-account-key.json')
    project_id = os.getenv('GCP_PROJECT_ID')

    if not project_id:
        print("ERROR: GCP_PROJECT_ID not set in .env")
        return False

    print(f"Setting up for project: {project_id}")

    # Set GOOGLE_APPLICATION_CREDENTIALS environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"Set GOOGLE_APPLICATION_CREDENTIALS to: {credentials_path}")

    # Verify credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        print("✓ Service account credentials loaded")
    except Exception as e:
        print(f"✗ Failed to load credentials: {e}")
        return False

    # Create Pub/Sub client
    try:
        publisher = pubsub_v1.PublisherClient(credentials=credentials)
        subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
        print("✓ Pub/Sub clients created")
    except Exception as e:
        print(f"✗ Failed to create Pub/Sub clients: {e}")
        return False

    # Create topic
    topic_name = 'gmail-notifications'
    topic_path = publisher.topic_path(project_id, topic_name)

    try:
        topic = publisher.create_topic(request={"name": topic_path})
        print(f"✓ Created Pub/Sub topic: {topic.name}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"✓ Pub/Sub topic already exists: {topic_path}")
        else:
            print(f"✗ Failed to create topic: {e}")
            return False

    # Create subscription
    subscription_name = 'gmail-notifications-sub'
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    # For local development, we'll create a pull subscription instead of push
    # Push subscriptions require HTTPS endpoints
    try:
        subscription = subscriber.create_subscription(
            request={
                "name": subscription_path,
                "topic": topic_path,
                # Remove push_config for pull subscription
            }
        )
        print(f"✓ Created Pub/Sub subscription: {subscription.name}")
        print("   Note: Using pull subscription for local development")
        print("   Webhook endpoint will need to be configured separately for production")
    except Exception as e:
        if "already exists" in str(e):
            print(f"✓ Pub/Sub subscription already exists: {subscription_path}")
        else:
            print(f"✗ Failed to create subscription: {e}")
            return False

    print("\n✅ Pub/Sub setup complete!")
    print("You can now run: python scripts/setup_gmail_watch.py")
    return True

if __name__ == "__main__":
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()

    setup_adc_and_pubsub()