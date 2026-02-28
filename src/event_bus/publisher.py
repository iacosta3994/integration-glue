"""Event Publisher

Publishes standardized events to various targets (message queue, HTTP endpoint, etc.).
"""

import json
from typing import Optional, List
from abc import ABC, abstractmethod

from .schema import StandardEvent


class EventPublisher(ABC):
    """Base class for event publishers."""
    
    @abstractmethod
    def publish(self, event: StandardEvent) -> bool:
        """Publish event to target.
        
        Args:
            event: StandardEvent to publish
            
        Returns:
            True if successful, False otherwise
        """
        pass


class ConsolePublisher(EventPublisher):
    """Publishes events to console (for testing/debugging)."""
    
    def publish(self, event: StandardEvent) -> bool:
        """Print event to console."""
        print("=" * 80)
        print(f"Event: {event.type.value}")
        print(f"Source: {event.source}")
        print(f"Actor: {event.actor.username}")
        print(f"Repository: {event.repository.full_name}")
        print(f"Timestamp: {event.timestamp}")
        print("-" * 80)
        print(json.dumps(event.to_dict(), indent=2))
        print("=" * 80)
        return True


class HTTPPublisher(EventPublisher):
    """Publishes events to HTTP endpoint."""
    
    def __init__(self, endpoint_url: str, headers: Optional[dict] = None):
        """Initialize HTTP publisher.
        
        Args:
            endpoint_url: Target HTTP endpoint
            headers: Optional headers to include
        """
        self.endpoint_url = endpoint_url
        self.headers = headers or {'Content-Type': 'application/json'}
    
    def publish(self, event: StandardEvent) -> bool:
        """POST event to HTTP endpoint."""
        import requests
        
        try:
            response = requests.post(
                self.endpoint_url,
                json=event.to_dict(),
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to publish event: {e}")
            return False


class MessageQueuePublisher(EventPublisher):
    """Publishes events to message queue (RabbitMQ, Kafka, etc.)."""
    
    def __init__(self, queue_config: dict):
        """Initialize message queue publisher.
        
        Args:
            queue_config: Configuration for message queue
        """
        self.queue_config = queue_config
        # Implementation depends on specific message queue
    
    def publish(self, event: StandardEvent) -> bool:
        """Publish event to message queue."""
        # Placeholder - implement based on specific queue
        raise NotImplementedError("Message queue publishing not yet implemented")


class MultiPublisher(EventPublisher):
    """Publishes events to multiple targets."""
    
    def __init__(self, publishers: List[EventPublisher]):
        """Initialize multi-publisher.
        
        Args:
            publishers: List of publishers to use
        """
        self.publishers = publishers
    
    def publish(self, event: StandardEvent) -> bool:
        """Publish to all configured publishers."""
        results = [publisher.publish(event) for publisher in self.publishers]
        return all(results)
