import utils
from pymessenger.bot import Bot
from pymessenger import Element, Button


class user():

    def __init__(self, user_json, user_id):
        self.first_name = user_json["first_name"]
        self.last_name = user_json["last_name"]
        self.profile_pic = user_json["profile_pic"]
        self.gender = user_json["gender"]
        self.id = user_id


def handle_message(raw_event):

    user_id = raw_event["sender"]["id"]
    bot = Bot(utils.config["page_access_token"])
    #current_user = user(bot.get_user_info(user_id), user_id)

    # the facebook ID of the person sending you the message

    message = raw_event["message"]["text"]  # the message's text]

    permission_url = ("https://www.facebook.com/v2.8/dialog/oauth?client_id=" +
                      "1734816396785509&scope=user_friends" + "" +
                      "&redirect_uri=" + "https://8f6438b2.ngrok.io/fb_" +
                      "callback?id=" + user_id)
    elements = []
    element = Element(title="Let undercover.chat look at your friend list.",
                      image_url=("http://static1.businessinsider.com/image/" +
                                 "559cec8e371d2254008b5ea2/facebook-friend" +
                                 "s-logo-wide.gif"),
                      subtitle="(We will never post as you)",
                      item_url=permission_url)
    elements.append(element)
    bot.send_generic_message(user_id, elements)
    bot.send_text_message(user_id, "Hello, welcome to undercover.chat!")
    bot.send_text_message(
        user_id, ("We let you talk with a random Facebook friend anonymously for" +
                  " 30 messages. Then you both vote to share your profile " +
                  "with each other. It only gets shared if both people agree" +
                  " to share it."))


def handle_delivery(raw_event):
    return 0


def handle_optin(raw_event):
    return 0


def handle_postback(raw_event):
    return 0


def handle_reads(raw_event):
    return 0


def handle_event(raw_event):
    if raw_event.get("message"):  # someone sent us a message
        handle_message(raw_event)

    if raw_event.get("delivery"):  # delivery confirmation
        handle_message(raw_event)

    if raw_event.get("optin"):  # optin confirmation
        handle_optin(raw_event)

    # user clicked/tapped "postback" button in earlier message
    if raw_event.get("postback"):
        handle_postback(raw_event)

    if raw_event.get("reads"):
        handle_reads(raw_event)
