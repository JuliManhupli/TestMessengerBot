import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

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
    print(data)

    if not data:
        return 'Bad request', 400

    try:
        messaging_events = data['entry'][0]['messaging']
        for event in messaging_events:
            print("Processing event:", event)
            if 'message' in event:
                user_id = event['sender']['id']
                text_input = event['message'].get('text')
                if text_input:
                    print(f"Message from user ID: {user_id} with text: {text_input}")
                    if text_input.lower() == "start":
                        send_start_template(user_id)
                    else:
                        send_message(user_id, text_input)
            elif 'postback' in event:
                user_id = event['sender']['id']
                payload = event['postback'].get('payload')
                if payload:
                    handle_postback(user_id, payload)
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
            'https://graph.facebook.com/v21.0/me/messages',
            params={'access_token': PAGE_ACCESS_TOKEN},
            headers={'Content-Type': 'application/json'},
            json=bot_response
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return None

def send_start_template(recipient_id):
    generic_template_response = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Привіт! Я демо бот Savvy 😃",
                            "image_url": "https://savvysolutions.ltd/_next/static/media/logo.0aa3c3fa.svg",
                            "subtitle": "Ось наше головне меню:",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Отримати фішки",
                                    "payload": "GET_CHIPS"
                                },
                                {
                                    "type": "postback",
                                    "title": "Використати фішки",
                                    "payload": "POST_CHIPS"
                                },
                                {
                                    "type": "postback",
                                    "title": "Баланс фішок",
                                    "payload": "CHIPS_BALANCE"
                                },
                            ]
                        },
                    ]
                }
            }
        }
    }
    try:
        response = requests.post(
            'https://graph.facebook.com/v21.0/me/messages',
            params={'access_token': PAGE_ACCESS_TOKEN},
            headers={'Content-Type': 'application/json'},
            json=generic_template_response
        )
        response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending generic template: {e}")
        return None

def handle_postback(user_id, payload):
    if payload == "GET_CHIPS":
        send_message(user_id, "Ви натиснули на кнопку 'Отримати фішки'!")
    elif payload == "POST_CHIPS":
        send_message(user_id, "Ви натиснули на кнопку 'Використати фішки'!")
    elif payload == "CHIPS_BALANCE":
        send_message(user_id, "Ви натиснули на кнопку 'Баланс фішок'!")
    else:
        send_message(user_id, "Unknown postback received.")

def set_persistent_menu():
    print("set_persistent_menu")
    persistent_menu_data = {

            "commands": [
                {
                    "locale": "default",
                    "commands": [
                        {
                            "name": "start",
                            "description": "Натисність сюди щоб почати користуватися ботом"
                        }
                    ]
                }
            ]

    }
    try:
        response = requests.post(
            'https://graph.facebook.com/v21.0/me/messenger_profile',
            params={'access_token': PAGE_ACCESS_TOKEN},
            headers={'Content-Type': 'application/json'},
            json=persistent_menu_data
        )
        response.raise_for_status()
        print("Persistent menu set successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error setting persistent menu: {e}")

if __name__ == '__main__':
    set_persistent_menu()
    app.run(debug=True, port=8000)
