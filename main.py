# Import the required modules
import telebot # Telegram bot library
from gtts import gTTS # Google Text-to-Speech library
import speech_recognition as sr # Speech recognition library
import os # Operating system library

# Create a bot object with the token
TOKEN = "5897098259:AAHTZ8n-pjGkCdr8K6sjfXZLF6gKB1To7vU"
bot = telebot.TeleBot(TOKEN)

# Define a handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    # Send a welcome message to the user
    bot.send_message(message.chat.id, "Hello, I am a chat telegram bot. I can do some cool things like converting text to speech and speech to text. Just type /help to see what I can do.")

# Define a handler for the /help command
@bot.message_handler(commands=['help'])
def help(message):
    # Send a help message to the user
    bot.send_message(message.chat.id, "Here are some commands and features that I support:\n"
                                      "/tts <message>: Convert your text into voice and send it as an audio message.\n"
                                      "/audio_to_text: Convert your audio message into text and send it as a message.\n"
                                      "If you send me any other text, I will reply with some custom messages.")

# Define a handler for the /tts command
@bot.message_handler(commands=['tts'])
def tts(message):
    # Get the text from the message after the command
    text = message.text[5:]

    # Check if the text is not empty
    if text:
        # Create a tts object with the text and the language
        tts = gTTS(text, lang='en')

        # Save the audio file in a temporary file
        audio_file = "temp.mp3"
        tts.save(audio_file)

        # Send the audio file as a voice message
        bot.send_voice(message.chat.id, open(audio_file, 'rb'))

        # Delete the temporary file
        os.remove(audio_file)
    else:
        # Send an error message if the text is empty
        bot.send_message(message.chat.id, "Please provide some text after the command.")

# Define a handler for the /audio_to_text command
@bot.message_handler(commands=['audio_to_text'])
def audio_to_text(message):
    # Send a message to the user to ask for an audio message
    bot.send_message(message.chat.id, "Please send me an audio message (maximum 1 minute) that you want me to convert into text.")

    # Define a sub-handler for the voice messages
    @bot.message_handler(content_types=['voice'])
    def voice(message):
        # Get the voice file from the message
        voice_file = message.voice

        # Download the voice file to a temporary file
        temp_file = bot.download_file(bot.get_file(voice_file.file_id).file_path)
        with open('temp.ogg', 'wb') as f:
            f.write(temp_file)

        # Create a speech recognizer object
        r = sr.Recognizer()

        # Load the voice file and convert it to wav format
        with sr.AudioFile('temp.ogg') as source:
            audio = r.record(source)
            os.system('ffmpeg -i temp.ogg temp.wav')

        # Recognize the speech using Google API
        try:
            text = r.recognize_google(audio, language='en')
            # Send the recognized text as a message
            bot.send_message(message.chat.id, f"I recognized this text from your audio: {text}")
        except sr.UnknownValueError:
            # Send an error message if the speech is not recognized
            bot.send_message(message.chat.id, "Sorry, I could not understand your audio.")
        except sr.RequestError as e:
            # Send an error message if there is a problem with the API
            bot.send_message(message.chat.id, f"Sorry, there was an error with the Google API: {e}")

        # Delete the temporary files
        os.remove('temp.ogg')
        os.remove('temp.wav')

# Define a handler for all other text messages
@bot.message_handler(content_types=['text'])
def chat(message):
    # Get the text from the message
    text = message.text

    # Check if the text is not empty and not a command
    if text and not text.startswith('/'):
        # Define some custom messages to reply based on some keywords or phrases in the text
        custom_messages = {
            'hello': "Hi, nice to meet you.",
            'how are you': "I'm fine, thank you. How are you?",
            'what can you do': "I can do some cool things like converting text to speech and speech to text. Just type /help to see what I can do.",
            'who are you': "I am a chat telegram bot. I was created by a human using Python.",
            'bye': "Bye, have a nice day."
        }

        # Check if the text matches any of the keywords or phrases
        for key, value in custom_messages.items():
            if key.lower() in text.lower():
                # Send the corresponding custom message as a reply
                bot.send_message(message.chat.id, value)
                return

        # If the text does not match any of the keywords or phrases, send a default message
        bot.send_message(message.chat.id, "Sorry, I don't understand what you mean. Please try something else.")

# Start polling for updates
bot.polling()

