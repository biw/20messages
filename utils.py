import json
import requests

# open up the config file
with open("config.json") as config:
    config = json.loads(config.read())


def send_message(recipient_id, message_data):
    params = {
        "access_token": config["page_access_token"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": message_data
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    if r.status_code != 200:
        print("Status Code: '{0}'".format(r.status_code))
        print("Details: '{0}'".format(r.text))
