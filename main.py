from flask import Flask, request, redirect
from werkzeug.serving import run_simple

# local imports
import utils
import receiver
import requests
import messages
import json
from pymessenger.bot import Bot

app = Flask(__name__, template_folder='templates')
app.debug = utils.config["debug"]
app.secret_key = utils.config["session-secret"]


@app.route("/fb_callback", methods=["GET", "POST"])
def callback():
    if request.method == "POST":
        return post_callback()
    elif request.method == "GET":
        return get_callback()


def get_callback():
    data = request.args

    if data.get("hub.mode") == "subscribe" and data.get("hub.verify_token") == utils.config["app_key"]:
        return data.get("hub.challenge"), 200
    elif data.get("code") != None and len(data.get("code")) and data.get("id") != None:
        user_id = data.get("id")
        code = data.get("code")
        print("user_id", user_id)

        raw_data = requests.get("https://graph.facebook.com/v2.8/oauth/access_token?" +
                                "client_id=1734816396785509" +
                                "&redirect_uri=https://262981a7.ngrok.io/fb_callback?id=" + user_id +
                                "&client_secret=3ead994a2fd130e838ea2106361c256b" +
                                "&code=" + code).json()
        print(json.dumps(raw_data, indent=4))
        access_token = raw_data["access_token"]

        bot = Bot(utils.config["page_access_token"])

        cuser = messages.user(bot.get_user_info(
            user_id), user_id)

        cuser.set_api_key(access_token)

        utils.set_redis(user_id, cuser)
        messages.after_registering(user_id)
        return redirect("/bye", 303)
    else:
        return "q2", 404


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


if __name__ == "__main__":
    run_simple(utils.config["website"], utils.config["port"], app,
               use_reloader=True, use_debugger=True, use_evalex=True)
