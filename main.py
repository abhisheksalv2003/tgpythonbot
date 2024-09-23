import edge_tts
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Define available voices
voices = {
    'Emma (US)': 'en-US-EmmaNeural',
    'Jenny (US)': 'en-US-JennyNeural',
    'Guy (US)': 'en-US-GuyNeural',
    'Aria (US)': 'en-US-AriaNeural',
    'Swara (HI)': 'hi-IN-SwaraNeural',
    'Madhur (HI)': 'hi-IN-MadhurNeural',
}

# TTS Conversion
async def tts(file_name: str, toConvert: str, voice: str):
    communicate = edge_tts.Communicate(toConvert, voice=voice)
    await communicate.save(file_name)

async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text
    voice = context.user_data.get('voice', 'en-US-EmmaNeural')
    try:
        await tts(f'edge-tts.mp3', text_input, voice)
        await update.message.reply_text("Speech conversion successful")
        await update.message.reply_audio(audio=open('edge-tts.mp3', 'rb'))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Main start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# Main menu display
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English Voices", callback_data='lang_en')],
        [InlineKeyboardButton("Hindi Voices", callback_data='lang_hi')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Select a language category:', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text('Select a language category:', reply_markup=reply_markup)

# Voice selection via button callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'back_to_menu':
        await show_main_menu(update, context)
        return

    if query.data.startswith('lang_'):
        language = query.data.split('_')[1]
        if language == 'en':
            voice_list = [name for name in voices.keys() if 'US' in name]
        else:  # Hindi voices
            voice_list = [name for name in voices.keys() if 'HI' in name]
        
        keyboard = [
            [InlineKeyboardButton(name, callback_data=name) for name in voice_list],
            [InlineKeyboardButton("« Back to Menu", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f'Select a voice model:', reply_markup=reply_markup)

    else:
        voice = voices[query.data]
        context.user_data['voice'] = voice
        keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Selected voice model: {query.data}\n\nYou can now send text messages to convert to speech.", reply_markup=reply_markup)

# Main function to initialize the bot
def main():
    application = Application.builder().token('YOUR_BOT_TOKEN_HERE').build()

    # Handlers for different commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

    application.run_polling()

# Run the bot
if __name__ == '__main__':
    main()
