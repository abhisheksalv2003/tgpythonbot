```markdown
# Personal Text-to-Speech Telegram Bot

This is a simple personal Telegram bot that converts text to speech using Microsoft's Azure Edge Text-to-Speech (TTS) voices. The bot allows you to choose from various language models and send text to convert it into speech, which is then returned as an audio file.

## Features

- Converts text messages to speech using multiple voice models.
- Supports various languages, including English, Hindi, Tamil, Telugu, Kannada, Marathi, and more.
- Simple interface with easy-to-use commands and inline button-based voice selection.

## Prerequisites

- Python 3.7 or higher
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather).

## Setup

1. Clone the repository or download the bot script.
   
2. Install the required dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. Replace `'YOUR_BOT_TOKEN_HERE'` in the `main()` function with your Telegram bot token obtained from BotFather.

4. Run the bot:

   ```bash
   python bot.py
   ```

## How to Use

1. Start the bot by typing `/start` in your Telegram chat with the bot.

2. A menu will appear, allowing you to choose between various language categories:
   - **English Voices**
   - **Indian Languages**
   - **Multi-language Models**

3. Select a voice model by clicking the buttons in the menu. Once a voice is selected, you can send text messages, and the bot will return a speech version as an audio file.

4. To change the voice, type `/start` again to bring up the menu.

## Available Voices

- **English**: US, UK, AU, CA, IE accents.
- **Indian Languages**: Hindi, Tamil, Telugu, Kannada, Gujarati, Marathi, Bengali, Punjabi, Odia, Assamese.
- **Multi-language Models**: Multi-language speech models are available for more versatile needs.

## Requirements

The bot uses the following Python libraries:

- `python-telegram-bot==20.5`
- `edge-tts==1.2.2`

These libraries are included in the `requirements.txt` file. Install them using:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.

## Credits
author - https://t.me/abhishacks
- Powered by [Microsoft Azure Edge Text-to-Speech](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/).
- Telegram bot built with [python-telegram-bot](https://python-telegram-bot.org/).
```

### Instructions:
- Replace `python bot.py` with the actual filename of your bot script if it's different.
- You can also modify the `README.md` further based on any additional features or changes you implement in the future.
