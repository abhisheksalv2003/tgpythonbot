from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

app = Flask(__name__)
bot = Bot(token='5569132270:AAHvA5A8pnAu6Cpd5HqBQrBIJNkBqAgBgLQ')
dispatcher = Dispatcher(bot, None, workers=0)

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

@app.route('/', methods=['POST'])
def index():
    dispatcher.process_update(Update.de_json(request.get_json(force=True), bot))
    return ''

if __name__ == '__main__':
    app.run(port=3000)
    
