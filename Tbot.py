#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging
import json

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, PicklePersistence
from antpool_api import AntApi

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

API, SECRET, UNAME, COIN = range(4)

commands_reply_keyboard = [['/pool_stats', '/sub_overview', 'comando3']]


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        f'Hi {user.mention_markdown_v2()}\!\nI\'ll ask you some parameters to start pooling data from your AntPool account\.\nLet\'s go\! Send me your *ANTPOOL APIKEY* first:')
    return API


def settings(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /settings is issued."""
    update.message.reply_markdown_v2(
        f'IMPORTANT\!\! This command will overwrite the parameters previously stored\. You can cancel at any moment with /cancel \.\nFirstly send me your *ANTPOOL APIKEY*:')
    return API


def settings_apikey(update: Update, context: CallbackContext) -> int:
    """Setting the AntPool API KEY"""
    context.user_data['sign_key'] = update.message.text
    update.message.reply_text('Stored! Now I\'ll request you the API SECRET')
    return SECRET


def settings_api_secret(update: Update, context: CallbackContext) -> int:
    """Setting the AntPool API SECRET"""
    context.user_data['sign_SECRET'] = update.message.text
    update.message.reply_text(
        'Great! Now send me your AntPool account/subaccount username')
    return UNAME


def settings_uname(update: Update, context: CallbackContext) -> int:
    """Setting the AntPool UserName"""
    context.user_data['sign_id'] = update.message.text
    reply_keyboard = [['BTC', 'LTC', 'ZEC']]
    update.message.reply_text('Awesome! Just one step more. Pick the coin type you\'re mining.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    return COIN


def settings_coin(update: Update, context: CallbackContext) -> int:
    context.user_data['coin_type'] = update.message.text
    update.message.reply_text('That\'s all! Now you\'re able to fetch data from antpool.\nPick some command to start.',
                              reply_markup=ReplyKeyboardMarkup(commands_reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return ConversationHandler.END


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def pool_stats_command(update: Update, context: CallbackContext) -> None:
    """Fetch Ant Pool statistics"""
    antpool = AntApi()
    stats = json.loads(antpool.pool_stats(context.user_data).replace('.', ','))
    if stats['message'] == 'ok':
        stats = stats['data']
        update.message.reply_markdown_v2(
            f'__AntPool Statistics:__\n*Status: *{stats["poolStatus"]}\n*Hashrate: *{stats["poolHashrate"]}\n*Workers active: *{stats["activeWorkerNumber"]}\n*Network diff: *{stats["networkDiff"]}\n*Estimate Time: *{stats["estimateTime"]}\n*Current Round: *{stats["currentRound"]}\n*Total Share Number: *{stats["totalShareNumber"]}\n*Total Block Number: *{stats["totalBlockNumber"]}',
            reply_markup=ReplyKeyboardMarkup(commands_reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    else:
        update.message.reply_text(
            'Ups\! Request error encountered\. Check your settings and try again\!')


def sub_overview_command(update: Update, context: CallbackContext) -> None:
    """Fetch subaccount overview"""
    antpool = AntApi()
    account_ovv = json.loads(antpool.sub_overview(
        context.user_data).replace('.', ','))
    if account_ovv['message'] == 'ok':
        account_ovv = account_ovv['data']
        coin = context.user_data['coin_type']
        update.message.reply_markdown_v2(f'__{context.user_data["sign_id"]} overview:__\n*Unpaid Amount: *{account_ovv["unpaidAmount"]} _{coin}_\n*Yesterday Earnings: *{account_ovv["yesterdayAmount"]} _{coin}_\n*Total earnings: *{account_ovv["totalAmount"]} _{coin}_\n*Hashrate\[daily\]: *{account_ovv["hsLast1d"]}\n*Hashrate\[1h\]: *{account_ovv["hsLast1h"]}\n*Hashrate\[10m\]: *{account_ovv["hsLast10m"]}\n*Active Workers: *{account_ovv["activeWorkerNum"]}\n*Inactive Workers: *{account_ovv["inactiveWorkerNum"]}',
                                         reply_markup=ReplyKeyboardMarkup(commands_reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    else:
        update.message.reply_text(
            'Ups\! Request error encountered\. Check your settings and try again\!')


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and end the conversation"""
    user = update.message.from_user
    logger.info("User %s cancelled the conversation", user.first_name)
    update.message.reply_text(
        'Ok. You can do this later. No problem!', reply_markup=ReplyKeyboardRemove()
    )


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    TOKEN = os.environ["BOT_TOKEN"]
    NAME = os.environ["APP_NAME"]
    PORT = int(os.environ.get('PORT', '8443'))
    persistence_file = PicklePersistence(filename='bot_data/storedData')
    updater = Updater(TOKEN, persistence=persistence_file)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start', start), CommandHandler('settings', settings)],
        states={
            API: [MessageHandler(Filters.text & ~Filters.command, settings_apikey)],
            SECRET: [MessageHandler(Filters.text & ~Filters.command, settings_api_secret)],
            UNAME: [MessageHandler(Filters.text & ~Filters.command, settings_uname)],
            COIN: [MessageHandler(
                Filters.text & ~Filters.command, settings_coin)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        persistent=True,
        name='settings_conversation'
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("pool_stats", pool_stats_command))
    dispatcher.add_handler(CommandHandler(
        "sub_overview", sub_overview_command))

    # # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(CommandHandler("user",stored_settings_commands))

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{TOKEN}")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
