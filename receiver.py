from pymessenger.bot import Bot

# local import
import utils
import messages

import json


def handle_auth_message(user_id, code):
    # get the info used for all messages
    bot = Bot(utils.config["page_access_token"])
    cuser = utils.get_redis(user_id)
    new_user = False

    if cuser == None:
        cuser = messages.user(bot.get_user_info(user_id), user_id)
        new_user = True

    needs_update = cuser.needs_api_update
    cuser.needs_api_update = False
    cuser.set_api_key(code)
    utils.set_redis(user_id, cuser)

    if new_user:
        messages.after_registering(cuser)
    elif needs_update:
        messages.refresh_api_key()


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


def handle_message(raw_event):

    # get the info used for all messages
    bot = Bot(utils.config["page_access_token"])
    user_id = raw_event["sender"]["id"]
    cuser = messages.user(bot.get_user_info(user_id), user_id)

    red_user = utils.get_redis(cuser.id)

    # welcome message, user has not signed up yet
    if red_user == None:
        messages.intro_message(bot, cuser)
        return

    # if something is different between the user and the database user
    if red_user.is_different(cuser):
        utils.set_redis(cuser.id, red_user)

    elif red_user.looking_for_chat:
        messages.send_in_limbo(bot, red_user)

    elif red_user.in_chat:
        if "message" in raw_event.keys():
            raw_message = raw_event["message"]
            messages.handle_chat(bot, red_user, raw_message)
        else:
            bot.send_text_message(user_id, "You are in a chat currently")

    elif red_user.on_edge and not red_user.showed_id:
        messages.send_decision_message(bot, red_user)

    elif red_user.on_edge and red_user.showed_id:
        messages.waiting_for_decision(bot, red_user)

    elif not red_user.in_chat and not red_user.looking_for_chat and not red_user.on_edge:
        messages.send_starting_gate(bot, red_user)


def handle_delivery(raw_event):
    return


def handle_optin(raw_event):
    return


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
            found_chat = red_user.search_for_chat()

            bot.send_text_message(red_user.id, "Searching...")
            if found_chat:
                messages.found_chat_reply(bot, red_user, found_chat)

        elif red_user.looking_for_chat:
            messages.send_in_limbo(bot, red_user)

    elif payload == "decision_time_yes" or payload == "decision_time_no":
        if not red_user.on_edge:
            return

        other_user = utils.get_redis(red_user.in_chat_with)

        if payload == "decision_time_no":
            messages.decision_time_no(bot, red_user, other_user)
        else:
            if red_user.showed_id:
                messages.waiting_for_decision(bot, red_user)
                return
            messages.decision_time_yes(bot, red_user, other_user)

    elif payload == "start_message":
        handle_message(raw_event)


def handle_reads(raw_event):
    return
