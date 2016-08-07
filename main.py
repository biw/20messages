from flask import Flask, request, session, redirect, render_template
from flask_api import status
from werkzeug.serving import run_simple
import bcrypt
import pymysql.cursors
import json
import os
import requests
import sys

app_key = "ETy&^^ReC*R+Ynk*GD6YQVmyf!3TdYWS"
page_access_token = "EAAYpzmsUt2UBALSGW8fHpqOnUPEmJG4F2S2jGp4nZAAIXzmBykzDernSZCouqV2iakAzOxK35NrC1QzY1nU5acyRySEACTJ9EeHHEsWktIdQ7zZBmJytK93lL7lbW5kQovPex1k5mc5mATI1qjfkjz5vw9sms2mZAIoeTLcKEwZDZD"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# open up the config file
with open("config.json") as config:
    config = json.loads(config.read())

app = Flask(__name__, template_folder='templates')
app.debug = config["debug"]
app.secret_key = config["session-secret"]


@app.route("/fb_callback", methods=["GET", "POST"])
def callback():
    if request.method == "POST":
        return post_callback()
    elif request.method == "GET":
        return get_callback()


def get_callback():
    data = request.args

    if data.get("hub.mode") == "subscribe" and data.get("hub.verify_token") == app_key:
        return data.get("hub.challenge"), status.HTTP_200
    else:
        return "", status.HTTP_403_FORBIDDEN


def post_callback():
    data = request.get_json()
    eprint(data)

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook
                    # ID
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"][
                        "text"]  # the message's text

                    send_message(sender_id, "got it, thanks!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):
                    pass

                if messaging_event.get("reads"):
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    eprint("sending message to {recipient}: {text}".format(
        recipient=recipient_id, text=message_text))

    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != 200:
        eprint(r.status_code)
        eprint(r.text)


if __name__ == "__main__":
    run_simple(config["website"], config["port"], app,
               use_reloader=True, use_debugger=True, use_evalex=True)
