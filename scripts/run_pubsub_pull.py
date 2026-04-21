#!/usr/bin/env python3
"""
Pull messages from Pub/Sub subscription and forward to local FastAPI processing endpoint.

Usage: python scripts/run_pubsub_pull.py

This is intended for local development where a push subscription to an HTTPS endpoint
is not available. It pulls messages from the subscription, extracts the Gmail
message ID, posts to the `/api/v1/webhook/process-email` endpoint on the local API,
then acknowledges messages on success.
"""
import os
import time
import json
import base64
import requests
from dotenv import load_dotenv

try:
    from google.cloud import pubsub_v1
    from google.oauth2 import service_account
except Exception as e:
    print("Missing google-cloud-pubsub or auth packages:", e)
    raise


def load_settings():
    load_dotenv()
    project = os.getenv('GCP_PROJECT_ID')
    sub = os.getenv('GCP_PUBSUB_SUBSCRIPTION')
    creds_path = os.getenv('GCP_CREDENTIALS_PATH', './credentials/service-account-key.json')
    api_endpoint = os.getenv('LOCAL_API_ENDPOINT', 'http://localhost:8000')

    if not project or not sub:
        raise RuntimeError('GCP_PROJECT_ID and GCP_PUBSUB_SUBSCRIPTION must be set in .env')

    # Normalize subscription path
    if sub.startswith('projects/'):
        subscription_path = sub
    else:
        subscription_path = f"projects/{project}/subscriptions/{sub}"

    return project, subscription_path, creds_path, api_endpoint


def decode_message(message):
    # message is Pub/Sub ReceivedMessage proto dict when using pull
    data_b64 = message.message.data if hasattr(message, 'message') else message['message']['data']
    attrs = message.message.attributes if hasattr(message, 'message') else message['message'].get('attributes', {})

    decoded = None
    if data_b64:
        try:
            decoded = base64.b64decode(data_b64).decode('utf-8')
            # Gmail push messages usually put metadata in attributes; data may be empty
            try:
                decoded_json = json.loads(decoded)
            except Exception:
                decoded_json = decoded
        except Exception:
            decoded_json = data_b64
    else:
        decoded_json = None

    return decoded_json, attrs


def main():
    project, subscription_path, creds_path, api_endpoint = load_settings()

    print(f"Using subscription: {subscription_path}")
    credentials = service_account.Credentials.from_service_account_file(creds_path)
    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

    # Pull loop
    while True:
        try:
            response = subscriber.pull(request={
                'subscription': subscription_path,
                'max_messages': 10,
                'return_immediately': True
            })

            if not response.received_messages:
                print("No messages. Sleeping 5s...")
                time.sleep(5)
                continue

            ack_ids = []
            for received in response.received_messages:
                msg = received
                decoded, attrs = decode_message(received)

                # Try common attribute keys for Gmail message id
                message_id = None
                if isinstance(attrs, dict):
                    message_id = attrs.get('message_id') or attrs.get('messageId') or attrs.get('gmail_message_id')

                # If not in attributes, try decoded payload
                if not message_id and decoded:
                    try:
                        if isinstance(decoded, dict):
                            message_id = decoded.get('message', {}).get('attributes', {}).get('message_id')
                        else:
                            # if decoded is JSON string
                            obj = json.loads(decoded)
                            message_id = obj.get('message', {}).get('attributes', {}).get('message_id')
                    except Exception:
                        pass

                if not message_id:
                    print('Could not find Gmail message_id in message; skipping and acking')
                    ack_ids.append(received.ack_id)
                    continue

                print(f'Found Gmail message_id: {message_id} — forwarding to local API')

                # Post to local processing endpoint
                try:
                    resp = requests.post(f"{api_endpoint}/api/v1/webhook/process-email", json={"message_id": message_id}, timeout=20)
                    if resp.status_code == 200:
                        print(f"Processed {message_id}: {resp.json().get('classification')} @ {resp.json().get('confidence')}")
                        ack_ids.append(received.ack_id)
                    else:
                        print(f"Processing failed (status {resp.status_code}): {resp.text}")
                        # Do not ack; let message be retried
                except Exception as e:
                    print(f"Error posting to local API: {e}")
                    # Do not ack; will retry

            if ack_ids:
                subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})
                print(f"Acknowledged {len(ack_ids)} messages")

        except Exception as e:
            print('Error pulling messages:', str(e))
            time.sleep(5)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nStopped by user')
