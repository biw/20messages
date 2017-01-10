from flask import Flask, request, redirect
from werkzeug.serving import run_simple
import json

# local imports
import utils
import receiver

app = Flask(__name__, template_folder='templates')
app.debug = utils.config["debug"]


@app.route("/fb_callback", methods=["GET", "POST"])
def callback():
    if request.method == "POST":
        return post_callback()
    elif request.method == "GET":
        return get_callback()


def get_callback():
    data = request.args

    if(data.get("hub.mode") == "subscribe" and
            data.get("hub.verify_token") == utils.config["fb_verify_token"]):
        return data.get("hub.challenge"), 200

    elif(data.get("code") != None and
         len(data.get("code")) and data.get("id") != None):

        user_id = data.get("id")
        code = data.get("code")
        receiver.handle_auth_message(user_id, code)

        return redirect("https://20messages.com/return", 303)
    else:
        return "Something went wrong, please try again.", 404


def post_callback():
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for raw_event in entry["messaging"]:
                try:
                    receiver.handle_event(raw_event)
                except Exception as exc:
                    print("\033[93merror: " + str(exc) + "\033[0m")
                    pass

    return "ok", 200


@app.route("/bye")
def bye():
    return "Please return back to the 20messages chat window", 200


if __name__ == "__main__":
    run_simple("localhost", utils.config["port"], app,
               use_reloader=True, use_debugger=True, use_evalex=True)
