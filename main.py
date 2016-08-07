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
page_access_token = "EAAYpzmsUt2UBABvSyMBgPqriDAWjlV49k7ZC9doivITdKKlgx27GGz76Vd7y8EZCLllZAlEyoRu4g9zJncUdsZAvXW6BHUl2X84ZCsFkFxrKVPizbzM145eVEzFEahZAO8TqGMestK7xzPZAkiS3Lg7ZBaf4RfrAewZBli6aUP9pqzgZDZD"


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
    eprint("hot post callback")

if __name__ == "__main__":
    run_simple(config["website"], config["port"], app,
               use_reloader=True, use_debugger=True, use_evalex=True)
