"""Gmail API Service for reading and processing emails

This service handles:
1. Authentication with Gmail API using service account
2. Reading email content from message ID
3. Parsing email headers and body
4. Extracting attachments
5. Converting raw email data to ProcessedEmail format
"""

import base64
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import NotFound, PermissionDenied
import google.auth.transport.urllib3
import urllib3

from src.utils import get_logger, retry
from src.config import settings

logger = get_logger(__name__)

class GmailService:
    """Service for interacting with Gmail API"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        """Initialize Gmail service with credentials"""
        self.credentials = None
        self.user_id = "me"  # Use authenticated user's emails
        self._initialize_credentials()
    
    def _initialize_credentials(self) -> None:
        """Initialize Google service account credentials (lazy loading)"""
        try:
            # Load service account credentials from environment
            if settings.gcp_credentials_path:
                self.credentials = Credentials.from_service_account_file(
                    settings.gcp_credentials_path,
                    scopes=self.SCOPES
                )
                logger.info("Gmail service credentials loaded successfully")
            else:
                logger.warning(
                    "GCP_CREDENTIALS_PATH not set. "
                    "Gmail API calls may fail. "
                    "Set GCP_CREDENTIALS_PATH in .env"
                )
                self.credentials = None
        except Exception as e:
            logger.warning(f"Failed to load Gmail credentials: {str(e)}")
            logger.warning("GmailService will not be able to fetch emails until credentials are available")
            self.credentials = None
    
    @retry(max_attempts=3, delay=2.0)
    async def get_email_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch email details by message ID from Gmail API
        
        Args:
            message_id: Gmail message ID (from webhook)
            
        Returns:
            Dictionary containing email details or None if not found
        """
        try:
            if not self.credentials:
                logger.error("Gmail credentials not initialized")
                return None
            
            logger.info(f"Fetching email: {message_id}")
            
            # Build Gmail API URL
            url = (
                f"https://www.googleapis.com/gmail/v1/users/{self.user_id}/messages/{message_id}"
                f"?format=full"  # Get full message including headers and payload
            )
            
            # Make request
            http = urllib3.PoolManager()
            response = self._make_authenticated_request(http, url)
            
            if response.status == 404:
                logger.warning(f"Email not found: {message_id}")
                return None
            
            if response.status != 200:
                logger.error(
                    f"Gmail API error {response.status}: {response.data.decode()}"
                )
                return None
            
            # Parse response
            email_data = json.loads(response.data.decode())
            logger.info(f"Successfully fetched email: {message_id}")
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error fetching email {message_id}: {str(e)}")
            return None
    
    def _make_authenticated_request(
        self,
        http: urllib3.PoolManager,
        url: str
    ) -> urllib3.response.HTTPResponse:
        """
        Make authenticated request to Gmail API
        
        Args:
            http: urllib3 PoolManager
            url: API endpoint URL
            
        Returns:
            HTTP response
        """
        # Refresh credentials if needed
        if self.credentials.expired:
            request = Request()
            self.credentials.refresh(request)
        
        # Add authorization header
        headers = {
            'Authorization': f'Bearer {self.credentials.token}'
        }
        
        return http.request('GET', url, headers=headers)
    
    def parse_email_headers(self, email_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract email headers from Gmail API response
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            Dictionary of parsed headers
        """
        try:
            headers = {}
            
            # Extract headers array
            header_list = email_data.get("payload", {}).get("headers", [])
            
            for header in header_list:
                name = header.get("name", "").lower()
                value = header.get("value", "")
                
                # Store common headers
                if name in ["subject", "from", "to", "cc", "bcc", "date"]:
                    headers[name] = value
                elif name == "content-type":
                    headers["content_type"] = value
                elif name == "message-id":
                    headers["message_id"] = value
            
            # Add Gmail-specific fields
            headers["gmail_message_id"] = email_data.get("id", "")
            headers["gmail_thread_id"] = email_data.get("threadId", "")
            
            logger.debug(f"Extracted headers: {list(headers.keys())}")
            
            return headers
            
        except Exception as e:
            logger.error(f"Error parsing headers: {str(e)}")
            return {}
    
    def parse_email_body(self, email_data: Dict[str, Any]) -> str:
        """
        Extract email body from Gmail API response
        
        Handles both plain text and HTML emails
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            Decoded email body as string
        """
        try:
            body = ""
            payload = email_data.get("payload", {})
            
            # Check if email is multipart (has attachments or alternative views)
            if "parts" in payload:
                # Multipart: find text/plain or text/html
                for part in payload.get("parts", []):
                    mime_type = part.get("mimeType", "")
                    
                    # Prefer text/plain, fallback to text/html
                    if mime_type == "text/plain":
                        body = self._decode_payload(part)
                        break
                    elif mime_type == "text/html" and not body:
                        body = self._decode_payload(part)
                        # Strip HTML tags
                        body = self._strip_html_tags(body)
            else:
                # Simple email with single body
                body = self._decode_payload(payload)
            
            # Clean up body
            body = body.strip()
            
            logger.debug(f"Extracted body length: {len(body)} chars")
            
            return body
            
        except Exception as e:
            logger.error(f"Error parsing body: {str(e)}")
            return ""
    
    def _decode_payload(self, part: Dict[str, Any]) -> str:
        """
        Decode email payload from base64url encoding
        
        Args:
            part: Email part containing data
            
        Returns:
            Decoded string
        """
        try:
            data = part.get("body", {}).get("data", "")
            
            if not data:
                return ""
            
            # Gmail uses base64url encoding
            # Add padding if needed
            padding = 4 - len(data) % 4
            if padding != 4:
                data += '=' * padding
            
            # Decode
            decoded = base64.urlsafe_b64decode(data)
            
            return decoded.decode('utf-8', errors='replace')
            
        except Exception as e:
            logger.error(f"Error decoding payload: {str(e)}")
            return ""
    
    def _strip_html_tags(self, html: str) -> str:
        """
        Remove HTML tags from text
        
        Args:
            html: HTML string
            
        Returns:
            Text without HTML tags
        """
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        html = re.sub(r'<[^>]+>', '', html)
        
        # Decode HTML entities
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&quot;', '"')
        html = html.replace('&#39;', "'")
        html = html.replace('&amp;', '&')
        
        return html
    
    def get_attachment_info(self, email_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract attachment information from email
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            List of attachment metadata
        """
        try:
            attachments = []
            payload = email_data.get("payload", {})
            
            if "parts" not in payload:
                return attachments
            
            for part in payload.get("parts", []):
                filename = part.get("filename", "")
                mime_type = part.get("mimeType", "")
                
                # Skip if not an attachment
                if not filename or mime_type.startswith(("text/", "application/json")):
                    continue
                
                attachments.append({
                    "filename": filename,
                    "mime_type": mime_type,
                    "size": part.get("body", {}).get("size", 0),
                    "attachment_id": part.get("body", {}).get("attachmentId", "")
                })
            
            logger.debug(f"Found {len(attachments)} attachment(s)")
            
            return attachments
            
        except Exception as e:
            logger.error(f"Error extracting attachments: {str(e)}")
            return []
    
    def format_email_data(
        self,
        email_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format raw Gmail API data into clean structure for processing
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            Formatted email data ready for hybrid classifier
        """
        try:
            headers = self.parse_email_headers(email_data)
            body = self.parse_email_body(email_data)
            attachments = self.get_attachment_info(email_data)
            
            # Parse date
            date_str = headers.get("date", "")
            try:
                # Parse RFC 2822 date format
                from email.utils import parsedate_to_datetime
                received_date = parsedate_to_datetime(date_str)
            except:
                received_date = datetime.utcnow()
            
            # Format email data
            formatted = {
                "id": headers.get("gmail_message_id", ""),
                "threadId": headers.get("gmail_thread_id", ""),
                "subject": headers.get("subject", "[No Subject]"),
                "from": headers.get("from", ""),
                "to": headers.get("to", ""),
                "cc": headers.get("cc", ""),
                "bcc": headers.get("bcc", ""),
                "body": body,
                "received_date": received_date.isoformat(),
                "attachments": attachments,
                "labels": email_data.get("labelIds", [])
            }
            
            logger.info(
                f"Formatted email: {formatted['id'][:20]}... "
                f"from={formatted['from'][:30]}..."
            )
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting email data: {str(e)}")
            return {}


# Singleton instance
_gmail_service: Optional[GmailService] = None

def get_gmail_service() -> GmailService:
    """Get or create Gmail service singleton"""
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = GmailService()
    return _gmail_service
