import os
import edge_tts
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from aiohttp import web

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

# Get bot token and port from environment variables
TOKEN = os.getenv('BOT_TOKEN')
PORT = int(os.getenv('PORT', 8080))

if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")

# Basic web app route
async def handle(request):
    return web.Response(text="Bot is running!")

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
        if len(text_input) > 500:
            await update.message.reply_text("Text is too long. Please keep it under 500 characters.")
            return
            
        voice = context.user_data.get('voice', 'en-US-EmmaNeural')
        status_message = await update.message.reply_text("Converting text to speech...")
        
        file_name = f'speech_{update.effective_user.id}.mp3'
        success = await tts(file_name, text_input, voice)
        
        if success:
            with open(file_name, 'rb') as audio:
                await update.message.reply_audio(audio=audio)
            await status_message.delete()
            os.remove(file_name)
        else:
            await status_message.edit_text("Failed to convert text to speech. Please try again.")
    except Exception as e:
        await update.message.reply_text("An error occurred. Please try again later.")
    finally:
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)

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

async def main():
    # Setup web app
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    # Initialize bot
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

    # Start the bot
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main()
