import os
import edge_tts
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import time

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in environment variables")

# Define Admin IDs (for personal use, you can ignore this or keep it)
ADMIN_IDS = [922264108]  # Your user ID here

# Define available voices
voices = { 
    # Your voice dictionary (unchanged for brevity)
}

# TTS Conversion
async def tts(file_name: str, toConvert: str, voice: str):
    try:
        communicate = edge_tts.Communicate(toConvert, voice=voice)
        await communicate.save(file_name)
    except Exception as e:
        logger.error(f"Error in TTS conversion: {e}")
        raise

# Function to convert text to speech and send the audio
async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text_input = update.message.text
        voice = context.user_data.get('voice', 'en-US-EmmaNeural')  # Default voice
        file_name = f'edge-tts-{update.effective_user.id}.mp3'
        
        await tts(file_name, text_input, voice)
        
        with open(file_name, 'rb') as audio_file:
            await update.message.reply_audio(audio=audio_file)
        
        os.remove(file_name)  # Clean up the file after sending
    except Exception as e:
        logger.error(f"Error in convert_text_to_speech: {e}")
        await update.message.reply_text(f"An error occurred while converting text to speech. Please try again later.")

# Main start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        await update.message.reply_text(f"Welcome, {user.first_name}! Use the bot to convert text to speech. Select a voice model using the menu.")
        await show_main_menu(update, context)
    except Exception as e:
        logger.error(f"Error in start function: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

# Main menu display
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [InlineKeyboardButton("English Voices", callback_data='lang_en')],
            [InlineKeyboardButton("Indian Languages", callback_data='lang_in')],
            [InlineKeyboardButton("Multi-language Models", callback_data='lang_multi')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text('Select a language category:', reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text('Select a language category:', reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in show_main_menu: {e}")
        await (update.message or update.callback_query.message).reply_text("An error occurred. Please try again later.")

# Voice selection via button callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        if query.data == 'back_to_menu':
            await show_main_menu(update, context)
            return

        # Rest of the button handling code unchanged for brevity...
    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        await query.edit_message_text("An error occurred. Please try again later.")

# Main function to initialize the bot
def main():
    try:
        while True:  # Keep the bot running
            try:
                application = Application.builder().token(BOT_TOKEN).build()

                # Handlers for different commands and messages
                application.add_handler(CommandHandler("start", start))
                application.add_handler(CallbackQueryHandler(button))
                application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

                logger.info("Bot is starting...")
                application.run_polling()
            except Exception as e:
                logger.critical(f"Critical error in main function: {e}")
                time.sleep(5)  # Wait before restarting to avoid rapid failure loops
    except Exception as e:
        logger.critical(f"Failed to restart bot: {e}")

# Run the bot
if __name__ == '__main__':
    main()
