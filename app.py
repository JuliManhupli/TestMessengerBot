import os

import requests
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verify_token(request)
    else:
        return handle_incoming_messages(request)


def verify_token(request):
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return 'Invalid verification token', 400


def handle_incoming_messages(request):
    data = request.get_json()
    if not data:
        return 'Bad request', 400

    try:
        messaging_events = data['entry'][0]['messaging']
        for event in messaging_events:
            if 'message' in event:
                user_id = event['sender']['id']
                text_input = event['message'].get('text')
                if text_input:
                    print(f"Message from user ID: {user_id} with text: {text_input}")
                    send_message(user_id, text_input)
        return 'Message processed', 200
    except Exception as e:
        print(f"Error processing message: {e}")
        return 'Internal Server Error', 500


def send_message(recipient_id, response):
    bot_response = {
        'recipient': {'id': recipient_id},
        'message': {'text': response}
    }
    try:
        response = requests.post(
            'https://graph.facebook.com/v12.0/me/messages',
            params={'access_token': PAGE_ACCESS_TOKEN},
            headers={'Content-Type': 'application/json'},
            json=bot_response
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
