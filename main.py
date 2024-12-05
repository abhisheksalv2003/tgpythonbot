import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket
# Rest of the code remains the same as in the previous correction

# Remove the Dispatcher import line
# Remove import telegram.ext import Dispatcher

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

async def tts(text: str, voice: str):
    try:
        # Create a temporary file in /tmp (Vercel's writable directory)
        file_name = f'/tmp/speech_{hash(text)}.mp3'
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(file_name)
        return file_name
    except Exception as e:
        logging.error(f"TTS conversion error: {e}")
        return None

async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text_input = update.message.text
        if len(text_input) > 500:
            await update.message.reply_text("Text is too long. Please keep it under 500 characters.")
            return
            
        voice = context.user_data.get('voice', 'en-US-EmmaNeural')
        status_message = await update.message.reply_text("Converting text to speech...")
        
        file_path = await tts(text_input, voice)
        
        if file_path:
            with open(file_path, 'rb') as audio:
                await update.message.reply_audio(audio=audio)
            await status_message.delete()
            # Clean up the file after sending
            os.remove(file_path)
        else:
            await status_message.edit_text("Failed to convert text to speech. Please try again.")
    except Exception as e:
        logging.error(f"Text to speech conversion error: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")
    finally:
        # Ensure file cleanup
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

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

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_error(404)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_health_server():
    port = int(os.getenv('PORT', find_free_port()))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f'Health check server running on port {port}')
    httpd.serve_forever()

# Main execution
async def main():
    # Set up logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    # Start health check server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Get bot token from environment variable
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        raise ValueError("No BOT_TOKEN found in environment variables!")

    # Initialize bot application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
