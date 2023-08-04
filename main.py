import telebot

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TOKEN = '1786770221:AAFod1pA_sGe_vI-cXMINGFXLrmRyVn1dr8'

# Create an instance of the Telegram bot
bot = telebot.TeleBot(TOKEN)

# '/start' command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hello! How can I assist you?')

# '/help' command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "I'm a helpful chat bot. Please feel free to ask me anything!")

# Custom command '/greet'
@bot.message_handler(commands=['greet'])
def send_greeting(message):
    bot.reply_to(message, 'Hello there!')

# Custom command '/time'
@bot.message_handler(commands=['time'])
def send_time(message):
    import datetime
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    bot.reply_to(message, f"The current time is {current_time}")
# Custom command '/specific'
@bot.message_handler(commands=['1'])
def send_specific_message(message):
    bot.reply_to(message, "this is testing program")

# Chat message handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# Start the bot
bot.polling()
