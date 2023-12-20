import json
from flask import Flask, jsonify, request
import requests
import asyncio
import aiohttp
import random
import threading

from flask import Flask, request, jsonify
import graphene


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()


class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')
    user = graphene.Field(User)

    def resolve_hello(self, info):
        return 'Hello, world!'

    def resolve_user(self, info):
        return User(id="1", name="Chang Liu", email="cl4404@columbia.edu")


# mock
notifications = [
    {"id": 1, "message": "User 1 has a new post on label fun"},
    {"id": 2, "message": "User 3 comment on the post 3"},
    {"id": 3, "message": "User 4 delete the post 2"}
]

schema = graphene.Schema(query=Query)
app = Flask(__name__)

# url for 3 microservices
USERS_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"
CONTENT_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"
NOTIFICATION_SERVICE_URL = "https://fy9wy2be45.execute-api.us-east-2.amazonaws.com"

log_messages = []
# log variable


user_response = {'User1': "cl4404"}
content_response = {'aasl21049i323': "This is a test post"}
notification_response = {'notice2134': "Hello from a test"}

def log_response(service_name, response):
    # log_messages.append(f"Received response from {service_name}: {response.json()}")
    log_messages.append(f"Received response from {service_name}: {response}")


def sync_call():
    # sync_call
    user_response = requests.get(f"{USERS_SERVICE_URL}/api/users")
    user = {'message': "User1 : cl4404"}
    log_response("Users Service", user)

    content_response = requests.get(f"{CONTENT_SERVICE_URL}/api/content")
    content = {"message": "aasl21049i323 : This is a test post"}
    log_response("Content Service", content)

    notification_response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notification")
    notification = {'message': "notice2134 : Hello from a test"}
    log_response("Notification Service", notification)


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
        user_response = requests.get(f"{USERS_SERVICE_URL}/api/users")
        user = {'message': "User1 : cl4404"}
        log_response("Users Service", user)

    def call_content_service():
        content_response = requests.get(f"{CONTENT_SERVICE_URL}/api/content")
        content = {"message": "aasl21049i323 : This is a test post"}
        log_response("Content Service", content)

    def call_notification_service():
        notification_response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notification")
        notification = {'message': "notice2134 : Hello from a test"}
        log_response("Notification Service", notification)

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


@app.route("/api/external", methods=["GET"])
def external_call_endpoint():
    # get all information you need about your ip
    external_api_url = "https://ipapi.co/json"

    try:
        # send GET request to external API
        response = requests.get(external_api_url)

        # check success
        if response.status_code == 200:
            # send back as json
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to fetch data from external API"}), response.status_code

    except requests.RequestException as e:
        # process error
        return jsonify({"error": str(e)}), 500


@app.route("/api/middleware", methods=["GET"])
def middleware_endpoint():
    global log_messages
    log_messages = []
    user_response = requests.get(f"{USERS_SERVICE_URL}/api/users")
    user = user_response.json()
    user = {'message': "User1 : cl4404"}
    notification_response = requests.get(f"{NOTIFICATION_SERVICE_URL}/api/notification")
    notification = notification_response.json()
    notification = {'message': "notice2134 : Hello from a test"}
    log_messages.append(f"{user['message']} has a lot of posts: {notification['message']}")
    return jsonify(log_messages)


@app.route("/api/test", methods=["GET"])
def test_pipeline():
    return jsonify({"Success": "You have deployed it."}), 200


@app.route("/api/graphql", methods=["GET"])
def graphql_api():
    # query from post
    query = request.args.get("query")
    # execute query
    result = schema.execute(query)
    # return response
    return jsonify(result.data)


# get
@app.route("/api/notification", methods=["GET"])
def get_notifications():
    return jsonify(notifications)


@app.route("/api/notification/<int:notification_id>", methods=["GET"])
def get_notification(notification_id):
    notification = next((n for n in notifications if n["id"] == notification_id), None)
    if notification:
        return jsonify(notification)
    else:
        return jsonify({"error": "Notification not found"}), 404


# create
@app.route("/api/notification", methods=["POST"])
def create_notification():
    notification = request.json
    notifications.append(notification)
    return jsonify(notification), 201


# delete
@app.route("/api/notification/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    global notifications
    notifications = [n for n in notifications if n["id"] != notification_id]
    return jsonify({"message": "Notification deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
