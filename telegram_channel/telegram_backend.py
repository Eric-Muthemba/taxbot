from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import requests
import logging
import json
import time

# Enable logging
logging.basicConfig( format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO )
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

RUN = range(1)

TOKEN = "6983932576:AAEfSgj6acJq9iMoAh-_yfeh5E4WawLUkMM"
url = "http://127.0.0.1:8080/jobs/conversation/api/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat.id
    response = requests.request("POST",url=url,data={"channel":"Telegram","message":"reset",'channel_id':chat_id})
    print(response.text)
    response = response.json()
    await update.message.reply_text(response["message"], reply_markup=ReplyKeyboardRemove())

    return RUN

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat.id
    message = update.message.text.lower()
    response = requests.request("POST",url=url,data={"channel":"Telegram","message":message,'channel_id':chat_id})
    print(response.text)
    response = response.json()
    await update.message.reply_text(response["message"], reply_markup=ReplyKeyboardRemove())

    return RUN

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    chat_id = update.message.chat.id
    requests.request("POST", url=url, data={"channel": "Telegram", "message": "cancelled", 'channel_id': chat_id})
    await update.message.reply_text("Thanks for using our service.Welcome back.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    print("started")

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
    states={
            RUN: [MessageHandler(filters.TEXT & ~filters.COMMAND, run)],
           },
           fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

