import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# API key from Telegram
api_key = 'YOUR_API_KEY'

# Create the Updater and pass it your API key
updater = Updater(api_key)

# Create the dispatcher
dispatcher = updater.dispatcher

# Define custom reply messages
custom_reply_messages = {
    'hello': "Hello there! How can I help you today?",
    'hi': "Hi! What's up?",
    'good morning': "Good morning! Have a wonderful day ahead.",
    'good night': "Good night! Sleep well.",
}

# Define a function to handle messages
def handle_message(bot, update):
    # Check if the message text is in the custom reply messages dictionary
    if update.message.text in custom_reply_messages:
        # Send the corresponding reply message
        bot.send_message(chat_id=update.message.chat_id, text=custom_reply_messages[update.message.text])
    else:
        # If the message text is not in the custom reply messages dictionary, send a generic reply message
        bot.send_message(chat_id=update.message.chat_id, text="I don't understand.")

# Add a handler for the message event
dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Start the Updater
updater.start_polling()
