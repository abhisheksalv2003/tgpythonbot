import edge_tts
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Define Admin IDs (for personal use, you can ignore this or keep it)
ADMIN_IDS = [922264108]  # Your user ID here

# Define available voices
voices = {
    # English voices
    'Emma (US)': 'en-US-EmmaNeural',
    'Jenny (US)': 'en-US-JennyNeural',
    'Guy (US)': 'en-US-GuyNeural',
    'Aria (US)': 'en-US-AriaNeural',
    'Davis (US)': 'en-US-DavisNeural',
    'Jane (UK)': 'en-GB-SoniaNeural',
    'Ryan (UK)': 'en-GB-RyanNeural',
    'Libby (AU)': 'en-AU-NatashaNeural',
    'William (AU)': 'en-AU-WilliamNeural',
    'Linda (CA)': 'en-CA-LiamNeural',
    'Liam (CA)': 'en-CA-ClaraNeural',
    'Connor (IE)': 'en-IE-ConnorNeural',
    'Emily (IE)': 'en-IE-EmilyNeural',
    'Rosa (IN)': 'en-IN-NeerjaNeural',
    'Ravi (IN)': 'en-IN-PrabhatNeural',

    # Hindi
    'Swara (HI)': 'hi-IN-SwaraNeural',
    'Madhur (HI)': 'hi-IN-MadhurNeural',

    # Tamil
    'Pallavi (TA)': 'ta-IN-PallaviNeural',
    'Valluvar (TA)': 'ta-IN-ValluvarNeural',

    # Telugu
    'Mohan (TE)': 'te-IN-MohanNeural',
    'Shruti (TE)': 'te-IN-ShrutiNeural',

    # Malayalam
    'Sobhana (ML)': 'ml-IN-SobhanaNeural',
    'Midhun (ML)': 'ml-IN-MidhunNeural',

    # Kannada
    'Gagan (KN)': 'kn-IN-GaganNeural',
    'Sapna (KN)': 'kn-IN-SapnaNeural',

    # Gujarati
    'Dhwani (GU)': 'gu-IN-DhwaniNeural',
    'Niranjan (GU)': 'gu-IN-NiranjanNeural',

    # Marathi
    'Aarohi (MR)': 'mr-IN-AarohiNeural',
    'Manohar (MR)': 'mr-IN-ManoharNeural',

    # Bengali
    'Tanishaa (BN)': 'bn-IN-TanishaaNeural',
    'Bashkar (BN)': 'bn-IN-BashkarNeural',

    # Punjabi
    'Amala (PA)': 'pa-IN-AmaraNeural',
    'Gurdeep (PA)': 'pa-IN-GurdeepNeural',

    # Odia (Oriya)
    'Prachi (OR)': 'or-IN-PrachiNeural',
    'Manish (OR)': 'or-IN-ManishNeural',

    # Assamese
    'Nabanita (AS)': 'as-IN-NabanitaNeural',
    'Manish (AS)': 'as-IN-ManishNeural',
}

# TTS Conversion
async def tts(file_name: str, toConvert: str, voice: str):
    communicate = edge_tts.Communicate(toConvert, voice=voice)
    await communicate.save(file_name)

# Function to convert text to speech and send the audio
async def convert_text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text
    voice = context.user_data.get('voice', 'en-US-EmmaNeural')  # Default voice
    try:
        await tts(f'edge-tts.mp3', text_input, voice)
        await update.message.reply_text("Speech conversion successful")
        await update.message.reply_audio(audio=open('edge-tts.mp3', 'rb'))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Main start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Welcome, {user.first_name}! Use the bot to convert text to speech. Select a voice model using the menu.")

    await show_main_menu(update, context)

# Main menu display
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            voice_list = [name for name in voices.keys() if any(accent in name for accent in ['US', 'UK', 'AU', 'CA', 'IE', 'IN']) and 'Multi' not in name]
        elif language == 'in':
            voice_list = [name for name in voices.keys() if any(lang in name for lang in ['HI', 'TA', 'TE', 'ML', 'KN', 'GU', 'MR', 'BN', 'PA', 'OR', 'AS'])]
        else:  # multi-language models
            voice_list = [name for name in voices.keys() if 'Multi' in name]
        
        keyboard = [
            [InlineKeyboardButton(name, callback_data=name) for name in voice_list[:3]],
            [InlineKeyboardButton("Next", callback_data=f'next_{language}_0')],
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
    application = Application.builder().token('YOUR_BOT_TOKEN_HERE').build()  # Replace with your bot token

    # Handlers for different commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_text_to_speech))

    application.run_polling()

# Run the bot
if __name__ == '__main__':
    main()
