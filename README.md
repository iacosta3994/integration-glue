# Integration Glue

A webhook integration hub that transforms events from various platforms (GitHub, GitLab, Jira, etc.) into a standardized event schema for event bus processing.

## Features

- **Standardized Event Schema**: Common event format across all platforms
- **GitHub Integration**: Full support for GitHub webhooks including:
  - Push events (commits)
  - Pull requests (opened, closed, merged, reviewed)
  - Issues (opened, closed, updated)
  - Comments (issues and PRs)
  - Releases
- **Flexible Publishing**: Send events to multiple targets:
  - Console (for debugging)
  - HTTP endpoints
  - Message queues (RabbitMQ, Kafka)
- **Secure**: Webhook signature verification
- **Extensible**: Easy to add new platform integrations

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/iacosta3994/integration-glue.git
cd integration-glue

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
```

### Configuration

Edit `.env` file:

```env
GITHUB_WEBHOOK_SECRET=your-webhook-secret
EVENT_BUS_ENDPOINT=https://your-event-bus.example.com/events
EVENT_BUS_TOKEN=your-api-token
PORT=5000
```

### Running the Server

```bash
# Development
python -m src.api.flask_app

# Production with Gunicorn
gunicorn src.api.flask_app:app --bind 0.0.0.0:5000 --workers 4
```

## GitHub Webhook Setup

1. Go to your GitHub repository settings
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-domain.com/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret (same as in `.env`)
   - **Events**: Select events you want to receive:
     - Pushes
     - Pull requests
     - Issues
     - Issue comments
     - Pull request reviews
     - Releases

## Architecture

### Event Flow

```
GitHub → Webhook → Handler → Mapper → StandardEvent → Publisher → Target(s)
```

### Standardized Event Schema

All events are transformed into a common format:

```python
{
  "id": "unique-event-id",
  "type": "pr.opened",
  "source": "github",
  "timestamp": "2026-02-27T21:54:00Z",
  "actor": {
    "id": "123",
    "username": "iacosta3994",
    "email": "user@example.com"
  },
  "repository": {
    "id": "456",
    "name": "my-repo",
    "full_name": "iacosta3994/my-repo",
    "owner": "iacosta3994"
  },
  "metadata": {
    "pr_number": 42,
    "pr_title": "Add new feature",
    "pr_state": "open",
    "action": "opened"
  },
  "changes": [],
  "raw_payload": { ... }
}
```

### Supported Event Types

#### Code Events
- `code.push` - Code pushed to repository
- `code.commit` - Individual commits

#### Pull Request Events
- `pr.opened` - PR created
- `pr.closed` - PR closed without merging
- `pr.merged` - PR merged
- `pr.reopened` - PR reopened
- `pr.updated` - PR updated
- `pr.reviewed` - Review submitted
- `pr.review_requested` - Review requested
- `pr.comment` - Comment on PR

#### Issue Events
- `issue.opened` - Issue created
- `issue.closed` - Issue closed
- `issue.reopened` - Issue reopened
- `issue.updated` - Issue updated
- `issue.comment` - Comment on issue

#### Release Events
- `release.published` - Release published
- `release.created` - Release created
- `release.deleted` - Release deleted

## Project Structure

```
integration-glue/
├── src/
│   ├── api/
│   │   └── flask_app.py          # Flask API server
│   ├── event_bus/
│   │   ├── schema.py             # Standardized event schema
│   │   └── publisher.py          # Event publishers
│   └── github/
│       ├── webhook_handler.py    # GitHub webhook handler
│       └── mappers.py            # Event mappers
├── requirements.txt
├── .env.example
└── README.md
```

## Extending Integration Glue

### Adding a New Platform Integration

1. Create a new directory under `src/` (e.g., `src/gitlab/`)
2. Implement webhook handler similar to `GitHubWebhookHandler`
3. Create mappers to transform platform events to `StandardEvent`
4. Add new endpoint in `flask_app.py`

Example:

```python
# src/gitlab/webhook_handler.py
class GitLabWebhookHandler:
    def handle_request(self, headers, body):
        # Parse GitLab webhook
        # Return StandardEvent
        pass
```

### Adding a New Publisher

Extend the `EventPublisher` base class:

```python
from src.event_bus.publisher import EventPublisher

class SlackPublisher(EventPublisher):
    def publish(self, event: StandardEvent) -> bool:
        # Send to Slack
        pass
```

## Testing

Test webhook locally using ngrok:

```bash
# Start ngrok
ngrok http 5000

# Use the ngrok URL as your webhook URL in GitHub
# Example: https://abc123.ngrok.io/webhooks/github
```

## Security

- ✅ Webhook signature verification
- ✅ Secret token authentication
- ✅ HTTPS recommended for production
- ✅ Environment variable configuration

## License

MIT License - feel free to use this in your projects!

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
