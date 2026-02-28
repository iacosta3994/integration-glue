"""GitHub Webhook Handler

Processes GitHub webhook payloads and transforms them into standardized events.
"""

import hashlib
import hmac
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..event_bus.schema import StandardEvent, EventType, EventMetadata
from .mappers import (
    map_commit_event,
    map_pull_request_event,
    map_issue_event,
    map_push_event,
    map_release_event,
    map_issue_comment_event,
    map_pull_request_review_event
)


class GitHubWebhookHandler:
    """Handles incoming GitHub webhook events."""
    
    def __init__(self, secret: str):
        """Initialize handler with webhook secret.
        
        Args:
            secret: GitHub webhook secret for signature verification
        """
        self.secret = secret.encode('utf-8')
        self.event_mappers = {
            'push': map_push_event,
            'pull_request': map_pull_request_event,
            'issues': map_issue_event,
            'issue_comment': map_issue_comment_event,
            'pull_request_review': map_pull_request_review_event,
            'release': map_release_event,
        }
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature.
        
        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not signature or not signature.startswith('sha256='):
            return False
        
        expected_signature = hmac.new(
            self.secret,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        received_signature = signature[7:]  # Remove 'sha256=' prefix
        
        return hmac.compare_digest(expected_signature, received_signature)
    
    def process_webhook(self, 
                       event_type: str, 
                       payload: Dict[str, Any],
                       delivery_id: str) -> Optional[StandardEvent]:
        """Process GitHub webhook and convert to standard event.
        
        Args:
            event_type: GitHub event type (X-GitHub-Event header)
            payload: Webhook payload
            delivery_id: GitHub delivery ID (X-GitHub-Delivery header)
            
        Returns:
            StandardEvent or None if event type is not supported
        """
        mapper = self.event_mappers.get(event_type)
        
        if not mapper:
            print(f"Unsupported event type: {event_type}")
            return None
        
        try:
            standard_event = mapper(payload, delivery_id)
            return standard_event
        except Exception as e:
            print(f"Error mapping {event_type} event: {e}")
            raise
    
    def handle_request(self,
                      headers: Dict[str, str],
                      body: bytes) -> Optional[StandardEvent]:
        """Handle complete webhook request.
        
        Args:
            headers: Request headers
            body: Raw request body
            
        Returns:
            StandardEvent or None
            
        Raises:
            ValueError: If signature verification fails
        """
        # Verify signature
        signature = headers.get('X-Hub-Signature-256', '')
        if not self.verify_signature(body, signature):
            raise ValueError("Invalid webhook signature")
        
        # Parse payload
        payload = json.loads(body)
        
        # Get event type and delivery ID
        event_type = headers.get('X-GitHub-Event')
        delivery_id = headers.get('X-GitHub-Delivery')
        
        if not event_type or not delivery_id:
            raise ValueError("Missing required headers")
        
        return self.process_webhook(event_type, payload, delivery_id)
