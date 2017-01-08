from pymessenger.bot import Bot
from pymessenger import Element, Button

import utils
import requests


def get_user_from_profile_id(profile_id):
    string = "-" + str(profile_id)
    chat_id = utils.get_redis(string)
    cuser = utils.get_redis(chat_id)
    return cuser


class user():

    def __init__(self, user_json, user_id):

        self.first_name = user_json["first_name"]
        self.last_name = user_json["last_name"]
        self.profile_pic = user_json["profile_pic"]
        self.gender = user_json["gender"]
        self.id = user_id
        self.profile_id = ""
        self.in_chat = False
        self.looking_for_chat = False
        self.on_edge = False
        self.messages_left = 20
        self.showed_id = False

    def get_friendlist(self):

        req_string = ("https://graph.facebook.com/v2.8/me/friends?access_token="
                      + self.api_key)
        raw_list = requests.get(req_string).json()
        user_list = raw_list["data"]

        return user_list

    def set_api_key(self, key):
        self.api_key = key

        req_string = ("https://graph.facebook.com/v2.8/me?fields=id,name&access_token="
                      + self.api_key)

        self.profile_id = requests.get(req_string).json()["id"]
        print(self.profile_id, self.id)

        utils.set_redis("-" + str(self.profile_id), self.id)

    def is_different(self, other_user):
        different = False
        if self.first_name != other_user.first_name:
            different = True
            self.first_name = other_user.first_name

        if self.last_name != other_user.last_name:
            different = True
            self.last_name = other_user.last_name

        if self.profile_pic != other_user.profile_pic:
            different = True
            self.profile_pic = other_user.profile_pic

        if self.gender != other_user.gender:
            different = True
            self.gender = other_user.gender

        return different

    def set_looking_for_chat(self):
        self.looking_for_chat = True
        utils.set_redis(self.id, self)

    def search_for_chat(self):
        friendlist = self.get_friendlist()

        for raw_friend in friendlist:

            cuser = get_user_from_profile_id(raw_friend["id"])

            if cuser != None and cuser.looking_for_chat:
                cuser.looking_for_chat = False
                cuser.in_chat = True
                cuser.in_chat_with = self.id
                utils.set_redis(cuser.id, cuser)

                self.looking_for_chat = False
                self.in_chat = True
                self.in_chat_with = cuser.id
                utils.set_redis(self.id, self)
                return cuser.id

        return False


def intro_message(bot, cuser):

    permission_url = ("https://www.facebook.com/v2.8/dialog/oauth?client_id=" +
                      "1734816396785509&scope=user_friends" + "" +
                      "&response_type=code&redirect_uri=" + "https://262981a7.ngrok.io/fb_" +
                      "callback?id=" + cuser.id)
    elements = []
    element = Element(title="Let undercover.chat look at your friend list.",
                      image_url=("http://static1.businessinsider.com/image/" +
                                 "559cec8e371d2254008b5ea2/facebook-friend" +
                                 "s-logo-wide.gif"),
                      subtitle="(We will never post as you)",
                      item_url=permission_url)
    elements.append(element)
    bot.send_generic_message(cuser.id, elements)
    bot.send_text_message(cuser.id, "Hello, welcome to undercover.chat!")
    bot.send_text_message(
        cuser.id, ("We let you talk with a random Facebook friend anonymously for" +
                   " 30 messages. Then you both vote to share your profile " +
                   "with each other. It only gets shared if both people agree" +
                   " to share it."))

    bot.send_text_message(cuser.id, "Please click the link above 🔝")


def after_registering(user_id):

    bot = Bot(utils.config["page_access_token"])
    cuser = user(bot.get_user_info(
        user_id), user_id)

    bot.send_text_message(cuser.id, "You are now registered!")
    send_starting_gate(bot, cuser)


def send_starting_gate(bot, cuser):
    buttons = []
    button = Button(title='Start Undercover Chat',
                    type='postback', payload='starting_gate')
    buttons.append(button)
    text = 'Ready to get started?'
    result = bot.send_button_message(cuser.id, text, buttons)


def send_in_limbo(bot, cuser):
    bot.send_text_message(
        cuser.id, "Sorry! Still looking for friends! Try to invite them to undercover.chat!")


def send_decision_message(bot, cuser):
    buttons = []
    button = Button(title='Agree to share identy',
                    type='postback', payload='decision_time_yes')
    button = Button(title='don\'t agree to share identy',
                    type='postback', payload='decision_time_no')
    buttons.append(button)
    text = 'Ready to get started?'
    result = bot.send_button_message(cuser.id, text, buttons)


def waiting_for_decision(bot, cuser):
    bot.send_text_message(
        cuser.id, ("Waiting for the other user to share." +
                   " Pick the other option about to" +
                   " disconnect."))
