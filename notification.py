from flask import Flask, request, jsonify

app = Flask(__name__)

# mock
notifications = [
    {"id": 1, "message": "User 1 has a new post on label fun"},
    {"id": 2, "message": "User 3 comment on the post 3"},
    {"id": 3, "message": "User 4 delete the post 2"}
]


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


if __name__ == '__main__':
    app.run(debug=True)
