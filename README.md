# Telegram Deep Linking Bot

This is a Telegram bot that allows you to share files via deep links. Users need to join specified Telegram channels to access the files.

## Features

- Deep link to specific files (documents, videos, photos, audio).
- Check user subscription to specified channels before allowing access to files.
- Admin commands to manage files and channels.
- Broadcast notices to all users who have started the bot.

## Requirements

- Python 3.7+
- SQLite database
- A Telegram bot token from [BotFather](https://t.me/BotFather)
- API ID and Hash from [my.telegram.org](https://my.telegram.org)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/shinigami205/TelegramFileLinkBot.git
    cd TelegramFileLinkBot
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables:
    - Replace `api_id`, `api_hash`, `bot_token`, `admin_id`, and `DataBaseChannel_id` with your own credentials in the script.

5. Initialize the SQLite database:
    ```bash
    sqlite3 files.db < init_db.sql
    ```

6. Run the bot:
    ```bash
    python bot.py
    ```

## Bot Commands

### User Commands

- `/start` - Start the bot and verify channel subscription.
- `/start <parameter>` - Start the bot with a deep link parameter to get the specified file.

### Admin Commands

- `/addfile` - Add a file to the database (use in reply to a message with a document, video, photo, or audio).
- `/add_channel <@channel>` - Add a required channel for subscription.
- `/remove_channel <@channel>` - Remove a required channel for subscription.
- `/list_channels` - List all required channels.
- `/send_notice <message>` - Send a notice to all users who have started the bot.

## File Structure

- `bot.py` - The main bot script.
- `requirements.txt` - List of dependencies.
- `init_db.sql` - SQL script to initialize the SQLite database.
- `channels.json` - JSON file to store required channels.
- `users.json` - JSON file to store users who have started the bot.

## Usage

1. Admins can add files to the bot by replying to a message with `/addfile`.
2. Admins can manage required channels using `/add_channel`, `/remove_channel`, and `/list_channels`.
3. Users will be prompted to join required channels before they can access files.
4. Admins can send notices to all users using `/send_notice`.

## License

This project is licensed under the MIT License.


## Powered by Shinigami_110
