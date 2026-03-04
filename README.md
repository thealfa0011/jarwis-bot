# Telegram YouTube Downloader Bot

## Overview
This is a bot designed to download videos from YouTube and provide the user with direct download links via Telegram.

## Features
- Download videos in various formats.
- User-friendly commands.
- Supports multiple video qualities.
- Easy to deploy and configure.

## Requirements
- Python 3.x
- Pyrogram or python-telegram-bot for handling Telegram's API.
- youtube-dl or pytube for downloading YouTube videos.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/thealfa0011/jarwis-bot.git
   cd jarwis-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
- Start the bot using:
  ```bash
  python bot.py
  ```
- Interact with the bot on Telegram by using commands like `/start` and `/download <YouTube URL>`.

## Configuration
- Create a `.env` file and include your Telegram bot token:
  ```env
  BOT_TOKEN=your_bot_token_here
  ```
- Optionally, modify download settings in the `config.py` file.

## Contribution
Feel free to open issues or submit pull requests to improve the bot.

## License
This project is licensed under the MIT License.