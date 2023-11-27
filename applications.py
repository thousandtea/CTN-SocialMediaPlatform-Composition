from flask import Flask, jsonify, request
import requests
import asyncio
import aiohttp
import random
import threading
app = Flask(__name__)

# url for 3 microservices
USERS_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"
CONTENT_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"
NOTIFICATION_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"

log_messages = []
# log variable


def log_response(service_name, response):
    log_messages.append(f"Received response from {service_name}: {response.json()}")


def sync_call():
    # sync_call
    user_response = requests.get(f"{USERS_SERVICE_URL}/api/users")
    log_response("Users Service", user_response)

    content_response = requests.get(f"{CONTENT_SERVICE_URL}/api/content")
    log_response("Content Service", content_response)

    notification_response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notification")
    log_response("Notification Service", notification_response)


@app.route("/api/composite/sync_call", methods=["GET"])
def sync_call_endpoint():
    global log_messages
    log_messages = []  # empty log
    sync_call()
    return jsonify(log_messages)


def async_call():
    # async_call
    threads = []

    def call_user_service():
        response = requests.get(f"{USERS_SERVICE_URL}/api/users")
        log_response("Users Service", response)

    def call_content_service():
        response = requests.get(f"{CONTENT_SERVICE_URL}/api/content")
        log_response("Content Service", response)

    def call_notification_service():
        response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notification")
        log_response("Notification Service", response)

    # create thread and start
    threads.append(threading.Thread(target=call_user_service))
    threads.append(threading.Thread(target=call_content_service))
    threads.append(threading.Thread(target=call_notification_service))

    for thread in threads:
        thread.start()

    # wait for thread finished
    for thread in threads:
        thread.join()

@app.route("/api/composite/async_call", methods=["GET"])
def async_call_endpoint():
    global log_messages
    log_messages = []  # empty log
    async_call()
    return jsonify(log_messages)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)