"""Standardized Event Schema

Defines the common event format used across all integrations.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class EventType(Enum):
    """Standard event types across all platforms."""
    # Code events
    CODE_PUSH = "code.push"
    CODE_COMMIT = "code.commit"
    
    # Pull Request events
    PR_OPENED = "pr.opened"
    PR_CLOSED = "pr.closed"
    PR_MERGED = "pr.merged"
    PR_REOPENED = "pr.reopened"
    PR_UPDATED = "pr.updated"
    PR_REVIEWED = "pr.reviewed"
    PR_REVIEW_REQUESTED = "pr.review_requested"
    PR_COMMENT = "pr.comment"
    
    # Issue events
    ISSUE_OPENED = "issue.opened"
    ISSUE_CLOSED = "issue.closed"
    ISSUE_REOPENED = "issue.reopened"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_COMMENT = "issue.comment"
    
    # Release events
    RELEASE_PUBLISHED = "release.published"
    RELEASE_CREATED = "release.created"
    RELEASE_DELETED = "release.deleted"
    
    # Deployment events
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"


class ChangeType(Enum):
    """Types of changes that can occur."""
    COMMIT = "commit"
    FILE_ADD = "file.add"
    FILE_MODIFY = "file.modify"
    FILE_DELETE = "file.delete"


@dataclass
class Actor:
    """Person or system that triggered the event."""
    id: str
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class Repository:
    """Repository information."""
    id: str
    name: str
    full_name: str
    owner: str
    url: str
    default_branch: str = "main"


@dataclass
class Change:
    """Represents a single change (commit, file change, etc.)."""
    type: ChangeType
    id: str
    message: Optional[str] = None
    timestamp: Optional[str] = None
    author: Optional[Actor] = None
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_removed: List[str] = field(default_factory=list)


@dataclass
class EventMetadata:
    """Flexible metadata container for event-specific data."""
    # Git/Branch metadata
    ref: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    created: Optional[bool] = None
    deleted: Optional[bool] = None
    forced: Optional[bool] = None
    base_ref: Optional[str] = None
    compare_url: Optional[str] = None
    
    # PR metadata
    pr_number: Optional[int] = None
    pr_title: Optional[str] = None
    pr_state: Optional[str] = None
    pr_url: Optional[str] = None
    pr_merged: Optional[bool] = None
    pr_draft: Optional[bool] = None
    pr_base_ref: Optional[str] = None
    pr_head_ref: Optional[str] = None
    pr_author: Optional[str] = None
    
    # Issue metadata
    issue_number: Optional[int] = None
    issue_title: Optional[str] = None
    issue_state: Optional[str] = None
    issue_url: Optional[str] = None
    issue_author: Optional[str] = None
    
    # Comment metadata
    comment_id: Optional[int] = None
    comment_body: Optional[str] = None
    comment_url: Optional[str] = None
    
    # Review metadata
    review_id: Optional[int] = None
    review_state: Optional[str] = None
    review_body: Optional[str] = None
    review_url: Optional[str] = None
    
    # Release metadata
    release_id: Optional[int] = None
    release_name: Optional[str] = None
    release_tag: Optional[str] = None
    release_url: Optional[str] = None
    release_draft: Optional[bool] = None
    release_prerelease: Optional[bool] = None
    
    # Common metadata
    action: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    
    # Custom metadata
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StandardEvent:
    """Standardized event format used across all integrations."""
    id: str  # Unique event ID
    type: EventType  # Event type
    source: str  # Source platform (github, gitlab, jira, etc.)
    timestamp: str  # ISO 8601 timestamp
    actor: Actor  # Who triggered the event
    repository: Repository  # Repository info
    metadata: EventMetadata  # Event-specific metadata
    changes: List[Change] = field(default_factory=list)  # List of changes
    raw_payload: Dict[str, Any] = field(default_factory=dict)  # Original payload
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'source': self.source,
            'timestamp': self.timestamp,
            'actor': self.actor.__dict__,
            'repository': self.repository.__dict__,
            'metadata': self.metadata.__dict__,
            'changes': [change.__dict__ for change in self.changes],
            'raw_payload': self.raw_payload
        }
