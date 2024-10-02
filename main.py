import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from aiohttp import web
import edge_tts
import asyncio
from langdetect import detect
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the bot token and app URL from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
APP_URL = os.environ.get('APP_URL')

if not BOT_TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN and APP_URL must be set in environment variables")

# Define available voices
voices = {
    'en': ['en-US-EmmaNeural', 'en-US-GuyNeural', 'en-GB-SoniaNeural'],
    'hi': ['hi-IN-SwaraNeural', 'hi-IN-MadhurNeural'],
    'ta': ['ta-IN-PallaviNeural', 'ta-IN-ValluvarNeural'],
    'te': ['te-IN-ShrutiNeural', 'te-IN-MohanNeural'],
    'ml': ['ml-IN-SobhanaNeural', 'ml-IN-MidhunNeural'],
    'kn': ['kn-IN-GaganNeural', 'kn-IN-SapnaNeural'],
    'gu': ['gu-IN-DhwaniNeural', 'gu-IN-NiranjanNeural'],
    'mr': ['mr-IN-AarohiNeural', 'mr-IN-ManoharNeural'],
    'bn': ['bn-IN-TanishaaNeural', 'bn-IN-BashkarNeural'],
    'pa': ['pa-IN-AmaraNeural', 'pa-IN-GurdeepNeural'],
}

# TTS Conversion
async def tts(file_name: str, toConvert: str, voice: str):
    try:
        communicate = edge_tts.Communicate(toConvert, voice=voice)
        await communicate.save(file_name)
    except Exception as e:
        logger.error(f"TTS conversion failed: {str(e)}")
        raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"Hello {user.mention_html()}! 👋\n\n"
        "I'm an AI-powered Text-to-Speech bot. Here's what I can do:\n\n"
        "1️⃣ Convert text to speech in multiple languages\n"
        "2️⃣ Detect the language of your text automatically\n"
        "3️⃣ Allow you to choose from various voice options\n\n"
        "To get started, simply send me some text, and I'll convert it to speech!"
    )
    await update.message.reply_html(welcome_message)

async def handle_voice_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang, voice = query.data.split('_')
    context.user_data['voice'] = voice
    
    await query.edit_message_text(f"Great! I've set your preferred voice for {lang} to {voice}. You can now send me some text to convert to speech.")

async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text_input = update.message.text
        detected_lang = detect(text_input)
        
        if detected_lang not in voices:
            detected_lang = 'en'  # Default to English if language not supported
        
        if 'voice' not in context.user_data or context.user_data['voice'] not in voices[detected_lang]:
            # If no voice is set or the set voice doesn't match the detected language, ask user to choose
            keyboard = [
                [InlineKeyboardButton(voice, callback_data=f"{detected_lang}_{voice}") for voice in voices[detected_lang]]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"I detected the language as {detected_lang}. Please choose a voice:", reply_markup=reply_markup)
            return

        voice = context.user_data['voice']
        
        await update.message.reply_text(f"Converting your {detected_lang} text to speech using {voice}...")
        
        await tts('edge-tts.mp3', text_input, voice)
        
        with open('edge-tts.mp3', 'rb') as audio_file:
            await update.message.reply_audio(audio=audio_file)
        
        # Remove the file after sending
        os.remove('edge-tts.mp3')
        
        # Add a random encouraging message
        encouragements = [
            "Great choice of words! 👍",
            "I enjoyed converting that for you! 😊",
            "Your text was fascinating! 🌟",
            "Keep the interesting messages coming! 🚀",
            "I'm learning so much from our conversations! 🧠"
        ]
        await update.message.reply_text(random.choice(encouragements))
        
    except Exception as e:
        logger.error(f"Error in convert_text_to_speech: {str(e)}")
        await update.message.reply_text("An error occurred while processing your request. Please try again.")

async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")

# Set up the application
app = Application.builder().token(BOT_TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_voice_selection))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))
app.add_error_handler(error_handler)

# Webhook handler
async def webhook_handler(request):
    try:
        update = await Update.de_json(await request.json(), app.bot)
        await app.process_update(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}")
        return web.Response(status=500)

# Health check endpoint
async def health_check(request):
    return web.Response(text="Advanced TTS Bot is running")

# Set up the web application
async def setup_webapp():
    webapp = web.Application()
    webapp.router.add_post(f'/{BOT_TOKEN}', webhook_handler)
    webapp.router.add_get('/health', health_check)
    return webapp

# Main function to set up and run the application
async def main():
    webapp = await setup_webapp()
    
    # Set webhook
    await app.bot.set_webhook(url=f"{APP_URL}/{BOT_TOKEN}")
    
    # Start the web application
    return webapp

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(main(), host='0.0.0.0', port=port)
