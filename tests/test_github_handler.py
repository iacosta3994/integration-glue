"""Unit tests for GitHub webhook handler."""

import json
import pytest
from src.github.webhook_handler import GitHubWebhookHandler
from src.event_bus.schema import EventType


def test_push_event_mapping():
    """Test mapping of GitHub push event."""
    handler = GitHubWebhookHandler(secret='test-secret')
    
    payload = {
        'ref': 'refs/heads/main',
        'before': 'abc123',
        'after': 'def456',
        'pusher': {
            'id': 1,
            'login': 'testuser',
            'name': 'Test User',
            'email': 'test@example.com'
        },
        'repository': {
            'id': 123,
            'name': 'test-repo',
            'full_name': 'testuser/test-repo',
            'owner': {'login': 'testuser'},
            'html_url': 'https://github.com/testuser/test-repo',
            'default_branch': 'main'
        },
        'commits': [
            {
                'id': 'def456',
                'message': 'Test commit',
                'timestamp': '2026-02-27T21:00:00Z',
                'author': {
                    'username': 'testuser',
                    'name': 'Test User',
                    'email': 'test@example.com'
                },
                'added': ['file1.txt'],
                'modified': ['file2.txt'],
                'removed': []
            }
        ]
    }
    
    event = handler.process_webhook('push', payload, 'test-delivery-id')
    
    assert event is not None
    assert event.type == EventType.CODE_PUSH
    assert event.source == 'github'
    assert event.actor.username == 'testuser'
    assert event.repository.name == 'test-repo'
    assert len(event.changes) == 1
    assert event.metadata.ref == 'refs/heads/main'


def test_pull_request_opened():
    """Test mapping of PR opened event."""
    handler = GitHubWebhookHandler(secret='test-secret')
    
    payload = {
        'action': 'opened',
        'sender': {
            'id': 1,
            'login': 'testuser',
            'avatar_url': 'https://github.com/testuser.png'
        },
        'repository': {
            'id': 123,
            'name': 'test-repo',
            'full_name': 'testuser/test-repo',
            'owner': {'login': 'testuser'},
            'html_url': 'https://github.com/testuser/test-repo'
        },
        'pull_request': {
            'number': 42,
            'title': 'Add new feature',
            'state': 'open',
            'html_url': 'https://github.com/testuser/test-repo/pull/42',
            'merged': False,
            'draft': False,
            'user': {'login': 'testuser'},
            'base': {'ref': 'main'},
            'head': {'ref': 'feature-branch'},
            'labels': []
        }
    }
    
    event = handler.process_webhook('pull_request', payload, 'test-delivery-id')
    
    assert event is not None
    assert event.type == EventType.PR_OPENED
    assert event.metadata.pr_number == 42
    assert event.metadata.pr_title == 'Add new feature'
    assert event.metadata.pr_state == 'open'


def test_signature_verification():
    """Test webhook signature verification."""
    import hmac
    import hashlib
    
    secret = 'test-secret'
    handler = GitHubWebhookHandler(secret=secret)
    
    payload = b'{"test": "data"}'
    
    # Create valid signature
    signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    assert handler.verify_signature(payload, signature) == True
    
    # Test invalid signature
    assert handler.verify_signature(payload, 'sha256=invalid') == False
    assert handler.verify_signature(payload, '') == False
