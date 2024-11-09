import edge_tts
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Define available voices
voices = {
    # English voices
    'Emma (US)': 'en-US-EmmaNeural',
    'Jenny (US)': 'en-US-JennyNeural',
    'Guy (US)': 'en-US-GuyNeural',
    'Jane (UK)': 'en-GB-SoniaNeural',
    'Ryan (UK)': 'en-GB-RyanNeural',
    
    # Hindi voices
    'Swara (HI)': 'hi-IN-SwaraNeural',
    'Madhur (HI)': 'hi-IN-MadhurNeural',
    
    # Multi-language models
    'Emma (Multi)': 'en-US-EmmaMultilingualNeural',
    'Ava (Multi)': 'en-US-AvaMultilingualNeural',
}

async def tts(file_name: str, text: str, voice: str):
    try:
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(file_name)
        return True
    except Exception:
        return False

async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text_input = update.message.text
        if len(text_input) > 500:  # Limit text length to avoid timeouts
            await update.message.reply_text("Text is too long. Please keep it under 500 characters.")
            return
            
        voice = context.user_data.get('voice', 'en-US-EmmaNeural')
        status_message = await update.message.reply_text("Converting text to speech...")
        
        success = await tts('edge-tts.mp3', text_input, voice)
        if success:
            await update.message.reply_audio(audio=open('edge-tts.mp3', 'rb'))
            await status_message.delete()
        else:
            await status_message.edit_text("Failed to convert text to speech. Please try again.")
    except Exception as e:
        await update.message.reply_text("An error occurred. Please try again later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English Voices", callback_data='lang_en')],
        [InlineKeyboardButton("Hindi Voices", callback_data='lang_hi')],
        [InlineKeyboardButton("Multi-language Models", callback_data='lang_multi')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text('Select a language category:', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text('Select a language category:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'back_to_menu':
        await show_main_menu(update, context)
        return

    if query.data.startswith('lang_'):
        language = query.data.split('_')[1]
        if language == 'en':
            voice_list = [name for name in voices.keys() if 'US' in name or 'UK' in name]
        elif language == 'hi':
            voice_list = [name for name in voices.keys() if 'HI' in name]
        else:  # multi-language models
            voice_list = [name for name in voices.keys() if 'Multi' in name]
        
        keyboard = []
        for voice in voice_list:
            keyboard.append([InlineKeyboardButton(voice, callback_data=voice)])
        keyboard.append([InlineKeyboardButton("« Back to Menu", callback_data='back_to_menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text='Select a voice model:', reply_markup=reply_markup)
    else:
        voice = voices.get(query.data)
        if voice:
            context.user_data['voice'] = voice
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"Selected voice: {query.data}\nYou can now send text messages to convert to speech.",
                reply_markup=reply_markup
            )

def main():
    # Replace with your bot token
    application = Application.builder().token('YOUR_BOT_TOKEN').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
