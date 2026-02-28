"""Flask API for receiving webhooks.

Provides HTTP endpoints for webhook integrations.
"""

from flask import Flask, request, jsonify
import os

from ..github.webhook_handler import GitHubWebhookHandler
from ..event_bus.publisher import ConsolePublisher, MultiPublisher, HTTPPublisher


app = Flask(__name__)

# Initialize handlers and publishers
github_handler = GitHubWebhookHandler(
    secret=os.getenv('GITHUB_WEBHOOK_SECRET', 'your-secret-here')
)

# Configure publishers
publishers = [ConsolePublisher()]

# Add HTTP publisher if configured
if os.getenv('EVENT_BUS_ENDPOINT'):
    publishers.append(HTTPPublisher(
        endpoint_url=os.getenv('EVENT_BUS_ENDPOINT'),
        headers={'Authorization': f"Bearer {os.getenv('EVENT_BUS_TOKEN')}"}
    ))

event_publisher = MultiPublisher(publishers)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/webhooks/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    try:
        # Process webhook
        event = github_handler.handle_request(
            headers=dict(request.headers),
            body=request.get_data()
        )
        
        if not event:
            return jsonify({'status': 'ignored', 'message': 'Event type not supported'}), 200
        
        # Publish event
        success = event_publisher.publish(event)
        
        if success:
            return jsonify({
                'status': 'success',
                'event_id': event.id,
                'event_type': event.type.value
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to publish event'
            }), 500
            
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 401
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'false').lower() == 'true')
