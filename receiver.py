import utils
from pymessenger.bot import Bot
import pickle
import json

# local import
import messages


def handle_message(raw_event):

    # get the info used for all messages
    bot = Bot(utils.config["page_access_token"])
    cuser = messages.user(bot.get_user_info(
        raw_event["sender"]["id"]), raw_event["sender"]["id"])

    red_user = utils.get_redis(cuser.id)

    # welcome message, user has not signed up yet
    if red_user == None:
        messages.intro_message(bot, cuser)
        return

    # if something is different between the user and the database user
    if red_user.is_different(cuser):
        utils.set_redis(cuser.id, red_user)

    if red_user.looking_for_chat:
        user1 = utils.get_redis("1256977684325846")
        user2 = utils.get_redis("1062053993873789")
        user1.in_chat_with = user2.id
        user2.in_chat_with = user1.id
        user1.looking_for_chat = False
        user2.looking_for_chat = False
        user1.in_chat = True
        user2.in_chat = True
        utils.set_redis(user1.id, user1)
        utils.set_redis(user2.id, user2)
        messages.send_in_limbo(bot, red_user)

    if red_user.in_chat:
        other_user = utils.get_redis(red_user.in_chat_with)

        red_user.messages_left -= 1
        other_user.messages_left -= 1
        text = "undercover says '{0}'".format(raw_event["message"]["text"])

        if red_user.messages == 0:
            red_user.in_chat = False
            red_user.on_edge = True
            other_user.in_chat = False
            other_user.on_edge = True

        utils.set_redis(red_user.id, red_user)
        utils.set_redis(other_user.id, other_user)

        bot.send_text_message(other_user.id, text)
        bot.send_text_message(
            red_user.id, "'{0}' Messages Left".format(red_user.messages_left))
        bot.send_text_message(
            other_user.id, "'{0}' Messages Left".format(red_user.messages_left))
    if red_user.on_edge and not red_user.showed_id:
        messages.send_decision_message()

    if red_user.on_edge and red_user.showed_id:
        messages.waiting_for_decision(bot, red_user)

    if not red_user.in_chat and not red_user.looking_for_chat and not red_user.on_edge:
        messages.send_starting_gate(bot, red_user)


def handle_delivery(raw_event):
    return 0


def handle_optin(raw_event):
    return 0


def handle_postback(raw_event):
    bot = Bot(utils.config["page_access_token"])
    cuser = messages.user(bot.get_user_info(
        raw_event["sender"]["id"]), raw_event["sender"]["id"])

    payload = raw_event["postback"]["payload"]

    red_user = utils.get_redis(cuser.id)

    # if something is different between the user and the database user
    if red_user.is_different(cuser):
        utils.set_redis(cuser.id, red_user)

    if payload == "starting_gate":
        # and not red_user.looking_for_chat:
        if not red_user.in_chat and not red_user.looking_for_chat:

            red_user.set_looking_for_chat()
            bot.send_text_message(
                red_user.id, "Searching for someone to chat with...")
            found_chat = red_user.search_for_chat()

            if found_chat:
                bot.send_text_message(
                    red_user.id, "You are now connected with a friend.")
                bot.send_text_message(
                    red_user.id, "You have (20) messages left")

                bot.send_text_message(
                    found_chat, "You are now connected with a friend.")
                bot.send_text_message(
                    found_chat, "You have (20) messages left")

        elif red_user.looking_for_chat:
            messages.send_in_limbo(bot, red_user)

        elif red_user.in_chat:
            return
    elif payload == "decision_time_yes" or payload == "decision_time_no":
        if red_user.on_edge:
            other_user = utils.get_redis(red_user.in_chat_with)

            if payload == "decision_time_no":
                red_user.on_edge = False
                red_user.in_chat_with = ""
                utils.set_redis(red_user.id, red_user)

                other_user.on_edge = False
                other_user.in_chat_with = ""
                utils.set_redis(other_user.id, other_user)

                bot.send_text_message(
                    red_user.id, ("Both random parties did not agree to share." +
                                  "\nConnection Disconnected"))
                bot.send_text_message(
                    red_user.id, ("Both random parties did not agree to share." +
                                  "\nConnection Disconnected"))

            else:
                try:
                    print(red_user.showed_id)
                except:
                    red_user.showed_id = True
                    pass

                if red_user.showed_id:
                    messages.waiting_for_decision(bot, red_user)
                    return
                red_user.showed_id = True

                if other_user.showed_id == True:
                    other_user.showed_id = False
                    red_user.showed_id = False
                    red_user.on_edge = False
                    other_user.on_edge = False
                    red_user.in_chat_with = ""
                    other_user.in_chat_with = ""
                    utils.set_redis(other_user.id, other_user)
                    utils.set_redis(red_user.id, red_user)

                    bot.send_image_url(red_user.id, other_user.profile_pic)
                    bot.send_image_url(other_user.id, red_user.profile_pic)
                    output = "The user you were chatting with was {0} {1}"
                    bot.send_text_message(red_user.id, output.format(
                        other_user.first_name, other_user.last_name))
                    bot.send_text_message(other_user.id, output.format(
                        red_user.first_name, red_user.last_name))
                    second_out = "Your conversation on undercover.chat with them is over\n"
                    bot.send_text_message(red_user.id, second_out)
                    bot.send_text_message(other_user.id, second_out)
                    messages.send_starting_gate(bot, red_user)
                    messages.send_starting_gate(bot, other_user)
                else:
                    utils.set_redis(other_user.id, other_user)
                    utils.set_redis(red_user.id, red_user)
        else:
            return


def handle_reads(raw_event):
    return 0


def handle_event(raw_event):
    if raw_event.get("message"):  # someone sent us a message
        handle_message(raw_event)

    if raw_event.get("delivery"):  # delivery confirmation
        handle_delivery(raw_event)

    if raw_event.get("optin"):  # optin confirmation
        handle_optin(raw_event)

    # user clicked/tapped "postback" button in earlier message
    if raw_event.get("postback"):
        handle_postback(raw_event)

    if raw_event.get("reads"):
        handle_reads(raw_event)
