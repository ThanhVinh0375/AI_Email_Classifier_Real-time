#!/usr/bin/env python3
"""
Gmail Webhook Setup Guide
"""

import os
from dotenv import load_dotenv

def print_setup_guide():
    """Print the setup guide for Gmail webhook"""

    load_dotenv()

    project_id = os.getenv('GCP_PROJECT_ID', 'YOUR_PROJECT_ID')
    service_account_email = "email-classifier-service-213@gen-lang-client-0860833865.iam.gserviceaccount.com"

    print("🚀 GMAIL WEBHOOK SETUP GUIDE")
    print("=" * 50)

    print("\n📋 REQUIRED STEPS:")
    print("1. Enable Google Cloud APIs")
    print("2. Grant Service Account Permissions")
    print("3. Create Pub/Sub Resources")
    print("4. Configure Gmail API")

    print("\n🔧 STEP 1: ENABLE GOOGLE CLOUD APIs")
    print("Go to Google Cloud Console:")
    print(f"   https://console.cloud.google.com/apis/library?project={project_id}")
    print("\nEnable these APIs:")
    print("   ✅ Cloud Pub/Sub API")
    print("   ✅ Gmail API")
    print("   ✅ Google Cloud Resource Manager API")

    print("\n🔐 STEP 2: GRANT SERVICE ACCOUNT PERMISSIONS")
    print("Go to IAM & Admin > IAM:")
    print(f"   https://console.cloud.google.com/iam-admin/iam?project={project_id}")
    print(f"\nFind service account: {service_account_email}")
    print("Grant these roles:")
    print("   ✅ Pub/Sub Admin")
    print("   ✅ Gmail API Scope: https://www.googleapis.com/auth/gmail.readonly")

    print("\n📡 STEP 3: CREATE PUB/SUB RESOURCES")
    print("After enabling APIs, run:")
    print("   python scripts/setup_pubsub.py")

    print("\n📧 STEP 4: CONFIGURE GMAIL WATCH")
    print("After Pub/Sub setup, run:")
    print("   python scripts/setup_gmail_watch.py")

    print("\n🔍 VERIFICATION:")
    print("Check setup status:")
    print("   python scripts/setup_webhook_helper.py")

    print("\n🚀 START SERVICES:")
    print("   docker-compose up -d")

    print("\n📊 ACCESS DASHBOARD:")
    print("   http://localhost:8501")

    print("\n" + "=" * 50)
    print("⚠️  IMPORTANT NOTES:")
    print("• Wait 2-3 minutes after enabling APIs")
    print("• Service account needs domain-wide delegation for Gmail")
    print("• Webhook endpoint: http://localhost:8000/api/v1/webhook/gmail")
    print("• Check logs in ./logs/ directory")

if __name__ == "__main__":
    print_setup_guide()