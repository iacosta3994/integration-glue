"""GitHub Event Mappers

Maps GitHub webhook payloads to standardized event schema.
"""

from typing import Dict, Any, List
from datetime import datetime

from ..event_bus.schema import (
    StandardEvent,
    EventType,
    EventMetadata,
    Actor,
    Repository,
    Change,
    ChangeType
)


def extract_actor(user_data: Dict[str, Any]) -> Actor:
    """Extract actor information from GitHub user data."""
    return Actor(
        id=str(user_data['id']),
        username=user_data['login'],
        name=user_data.get('name'),
        email=user_data.get('email'),
        avatar_url=user_data.get('avatar_url')
    )


def extract_repository(repo_data: Dict[str, Any]) -> Repository:
    """Extract repository information from GitHub repo data."""
    return Repository(
        id=str(repo_data['id']),
        name=repo_data['name'],
        full_name=repo_data['full_name'],
        owner=repo_data['owner']['login'],
        url=repo_data['html_url'],
        default_branch=repo_data.get('default_branch', 'main')
    )


def map_push_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub push event to standard event."""
    commits = payload.get('commits', [])
    
    changes = []
    for commit in commits:
        changes.append(Change(
            type=ChangeType.COMMIT,
            id=commit['id'],
            message=commit['message'],
            timestamp=commit['timestamp'],
            author=Actor(
                id='',
                username=commit['author']['username'],
                name=commit['author']['name'],
                email=commit['author']['email']
            ),
            files_added=commit.get('added', []),
            files_modified=commit.get('modified', []),
            files_removed=commit.get('removed', [])
        ))
    
    return StandardEvent(
        id=delivery_id,
        type=EventType.CODE_PUSH,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['pusher']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            ref=payload['ref'],
            before=payload['before'],
            after=payload['after'],
            created=payload.get('created', False),
            deleted=payload.get('deleted', False),
            forced=payload.get('forced', False),
            base_ref=payload.get('base_ref'),
            compare_url=payload.get('compare')
        ),
        changes=changes,
        raw_payload=payload
    )


def map_pull_request_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub pull request event to standard event."""
    pr = payload['pull_request']
    action = payload['action']
    
    # Determine event type based on action
    event_type_map = {
        'opened': EventType.PR_OPENED,
        'closed': EventType.PR_MERGED if pr.get('merged') else EventType.PR_CLOSED,
        'reopened': EventType.PR_REOPENED,
        'synchronize': EventType.PR_UPDATED,
        'edited': EventType.PR_UPDATED,
        'review_requested': EventType.PR_REVIEW_REQUESTED,
    }
    
    event_type = event_type_map.get(action, EventType.PR_UPDATED)
    
    return StandardEvent(
        id=delivery_id,
        type=event_type,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['sender']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            pr_number=pr['number'],
            pr_title=pr['title'],
            pr_state=pr['state'],
            pr_url=pr['html_url'],
            pr_merged=pr.get('merged', False),
            pr_draft=pr.get('draft', False),
            pr_base_ref=pr['base']['ref'],
            pr_head_ref=pr['head']['ref'],
            pr_author=pr['user']['login'],
            action=action,
            labels=[label['name'] for label in pr.get('labels', [])]
        ),
        raw_payload=payload
    )


def map_issue_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub issue event to standard event."""
    issue = payload['issue']
    action = payload['action']
    
    event_type_map = {
        'opened': EventType.ISSUE_OPENED,
        'closed': EventType.ISSUE_CLOSED,
        'reopened': EventType.ISSUE_REOPENED,
        'edited': EventType.ISSUE_UPDATED,
        'assigned': EventType.ISSUE_UPDATED,
        'labeled': EventType.ISSUE_UPDATED,
    }
    
    event_type = event_type_map.get(action, EventType.ISSUE_UPDATED)
    
    return StandardEvent(
        id=delivery_id,
        type=event_type,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['sender']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            issue_number=issue['number'],
            issue_title=issue['title'],
            issue_state=issue['state'],
            issue_url=issue['html_url'],
            issue_author=issue['user']['login'],
            action=action,
            labels=[label['name'] for label in issue.get('labels', [])],
            assignees=[assignee['login'] for assignee in issue.get('assignees', [])]
        ),
        raw_payload=payload
    )


def map_issue_comment_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub issue comment event to standard event."""
    comment = payload['comment']
    issue = payload['issue']
    
    # Determine if this is a PR comment or issue comment
    is_pr = 'pull_request' in issue
    event_type = EventType.PR_COMMENT if is_pr else EventType.ISSUE_COMMENT
    
    return StandardEvent(
        id=delivery_id,
        type=event_type,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['sender']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            comment_id=comment['id'],
            comment_body=comment['body'],
            comment_url=comment['html_url'],
            issue_number=issue['number'],
            issue_title=issue['title'],
            action=payload['action']
        ),
        raw_payload=payload
    )


def map_pull_request_review_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub pull request review event to standard event."""
    review = payload['review']
    pr = payload['pull_request']
    
    return StandardEvent(
        id=delivery_id,
        type=EventType.PR_REVIEWED,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['sender']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            review_id=review['id'],
            review_state=review['state'],
            review_body=review.get('body', ''),
            review_url=review['html_url'],
            pr_number=pr['number'],
            pr_title=pr['title'],
            action=payload['action']
        ),
        raw_payload=payload
    )


def map_release_event(payload: Dict[str, Any], delivery_id: str) -> StandardEvent:
    """Map GitHub release event to standard event."""
    release = payload['release']
    
    return StandardEvent(
        id=delivery_id,
        type=EventType.RELEASE_PUBLISHED,
        source='github',
        timestamp=datetime.utcnow().isoformat(),
        actor=extract_actor(payload['sender']),
        repository=extract_repository(payload['repository']),
        metadata=EventMetadata(
            release_id=release['id'],
            release_name=release['name'],
            release_tag=release['tag_name'],
            release_url=release['html_url'],
            release_draft=release['draft'],
            release_prerelease=release['prerelease'],
            action=payload['action']
        ),
        raw_payload=payload
    )
