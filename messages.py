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
        self.needs_api_update = False

    def get_friendlist(self):

        req_string = ("https://graph.facebook.com/v2.8/me/friends?access_token="
                      + self.api_key)
        raw_list = requests.get(req_string).json()
        user_list = raw_list["data"]

        return user_list

    def set_api_key(self, code):

        raw_data = requests.get("https://graph.facebook.com/v2.8/oauth/" +
                                "access_token?client_id=" +
                                utils.config["fb_client_id"] +
                                "&redirect_uri=" + utils.config["website"] +
                                "/fb_callback?id=" + self.id + "&client_secret="
                                + utils.config["fb_client_secret"] + "&code=" +
                                code).json()

        access_token = raw_data["access_token"]

        self.api_key = access_token

        req_string = ("https://graph.facebook.com/v2.8/me?" +
                      "fields=id,name&access_token=" + self.api_key)

        self.profile_id = requests.get(req_string).json()["id"]
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
                      utils.config["fb_client_id"] + "&scope=user_friends" +
                      "&response_type=code&redirect_uri=" +
                      utils.config["website"] + "/fb_callback?id=" + cuser.id)
    elements = []
    element = Element(title="Let 20messages look at your friend list.",
                      image_url=("http://static1.businessinsider.com/image/" +
                                 "559cec8e371d2254008b5ea2/facebook-friend" +
                                 "s-logo-wide.gif"),
                      subtitle="(We will never post as you)",
                      item_url=permission_url)
    elements.append(element)
    bot.send_generic_message(cuser.id, elements)
    bot.send_text_message(cuser.id, "Hello, welcome to 20messages!")
    bot.send_text_message(
        cuser.id, ("We let you talk with a random Facebook friend anonymously for" +
                   " 20 messages. Then you both vote to share your profile " +
                   "with each other. It only gets shared if both people agree" +
                   " to share it."))

    bot.send_text_message(cuser.id, "Please click the link above 🔝")


def after_registering(cuser):
    bot = Bot(utils.config["page_access_token"])

    bot.send_text_message(cuser.id, "You are now registered!")
    send_starting_gate(bot, cuser)


def refresh_api_key(cuser):
    bot = Bot(utils.config["page_access_token"])

    bot.send_text_message(
        cuser.id, "The API was refreshed. Everthing looks good!")
    send_starting_gate(bot, cuser)


def send_starting_gate(bot, cuser):
    buttons = []
    button = Button(title='Start Chat',
                    type='postback', payload='starting_gate')
    buttons.append(button)
    text = 'Ready to get started?'
    result = bot.send_button_message(cuser.id, text, buttons)


def found_chat_reply(bot, cuser, other_id):
    text_1 = "You are now connected with a friend."
    text_2 = "You have 20 messages left"

    bot.send_text_message(cuser.id, text_1)
    bot.send_text_message(other_id, text_1)

    bot.send_text_message(cuser.id, text_2)
    bot.send_text_message(other_id, text_2)


def send_in_limbo(bot, cuser):
    bot.send_text_message(
        cuser.id, "Sorry! Still looking for friends! Try to invite them to 20messages!")


def send_decision_message(bot, cuser):
    text = 'Would you like to share your identy?'
    buttons = []
    button = Button(title='Yes',
                    type='postback', payload='decision_time_yes')
    buttons.append(button)
    button = Button(title='No',
                    type='postback', payload='decision_time_no')
    buttons.append(button)
    result = bot.send_button_message(cuser.id, text, buttons)


def waiting_for_decision(bot, cuser):
    bot.send_text_message(
        cuser.id, ("Waiting for the other user to share." +
                   " Pick the other option about to" +
                   " disconnect."))


def decision_time_no(bot, cuser, other_user):
    cuser.on_edge = False
    cuser.in_chat_with = ""
    utils.set_redis(cuser.id, cuser)

    other_user.on_edge = False
    other_user.in_chat_with = ""
    utils.set_redis(other_user.id, other_user)

    message_text = "Both random parties did not agree to share.\nConnection Disconnected"

    bot.send_text_message(cuser.id, message_text)
    bot.send_text_message(other_user.id, message_text)
    send_starting_gate(bot, cuser)
    send_starting_gate(bot, other_user)


def decision_time_yes(bot, cuser, other_user):
    cuser.showed_id = True

    # if the other user has not decided yet
    if not other_user.showed_id:
        utils.set_redis(cuser.id, cuser)
        return

    cuser.showed_id = False
    other_user.showed_id = False

    cuser.on_edge = False
    other_user.on_edge = False

    cuser.in_chat_with = ""
    other_user.in_chat_with = ""

    utils.set_redis(cuser.id, cuser)
    utils.set_redis(other_user.id, other_user)

    bot.send_image_url(cuser.id, other_user.profile_pic)
    bot.send_image_url(other_user.id, cuser.profile_pic)

    output = "You were chatting with {0} {1}!"
    bot.send_text_message(cuser.id, output.format(
        other_user.first_name, other_user.last_name))
    bot.send_text_message(other_user.id, output.format(
        cuser.first_name, cuser.last_name))

    second_out = "Your conversation on 20messages with them is over\n"
    bot.send_text_message(cuser.id, second_out)
    bot.send_text_message(other_user.id, second_out)

    send_starting_gate(bot, cuser)
    send_starting_gate(bot, other_user)


def handle_chat(bot, cuser, raw_message):
    other_user = utils.get_redis(cuser.in_chat_with)

    messages_display = cuser.messages_left
    cuser.messages_left -= 1
    other_user.messages_left -= 1

    messages_left = cuser.messages_left

    if messages_left == 0:
        cuser.in_chat = False
        cuser.on_edge = True
        other_user.in_chat = False
        other_user.on_edge = True
        cuser.messages_left = 20
        other_user.messages_left = 20

    utils.set_redis(cuser.id, cuser)
    utils.set_redis(other_user.id, other_user)

    if "text" in raw_message.keys():
        text_message = raw_message["text"]
        text = "{0}: '{1}'".format(messages_display, text_message)
        bot.send_text_message(other_user.id, text)

    elif "url" in raw_message["attachments"][0]["payload"].keys():
        img_url = raw_message["attachments"][0]["payload"]["url"]
        text = "{0}:".format(messages_display)

        bot.send_text_message(other_user.id, text)
        bot.send_image_url(other_user.id, img_url)

    if messages_left == 0:
        send_decision_message(bot, cuser)
        send_decision_message(bot, other_user)
    elif messages_left == 1:
        bot.send_text_message(cuser.id, "You have one message left!")
        bot.send_text_message(other_user.id, "You have one message left!")
