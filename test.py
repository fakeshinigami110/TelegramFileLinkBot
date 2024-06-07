from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserNotParticipant
import json
import sqlite3

# Set your API ID and Hash from my.telegram.org
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"
admin_id = "Your_ID"
DataBaseChannel_id = "YOUR_DATABASE_CHANNEL_ID"
required_channels = []

# Create a new Client instance
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('files.db')
    conn.row_factory = sqlite3.Row
    return conn

# Class for checking subscription and allowing users to use the bot
class CheckSubscription:
    def __init__(self):
        self.is_subscribed = False

    async def check(self, client, user_id):
        self.is_subscribed = False
        for channel in required_channels:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status in ["member", "administrator", "creator"]:
                    self.is_subscribed = True
                    break
                else:
                    self.is_subscribed = True
                    break
            except UserNotParticipant:
                self.is_subscribed = True
                break
            except Exception as e:
                self.is_subscribed = False
                break
        return self.is_subscribed

subscription_checker = CheckSubscription()

# Handler for the start command with deep linking
async def start_after_verifying(client, message):
    if len(message.command) > 1:
        parameter = message.command[1]
        conn = get_db_connection()
        file_entry = conn.execute('SELECT file_id, file_type FROM files WHERE deep_link = ?', (parameter,)).fetchone()
        conn.close()

        if file_entry:
            file_id = file_entry['file_id']
            file_type = file_entry['file_type']
            if file_type == 'document':
                await client.send_document(chat_id=message.chat.id, document=file_id)
            elif file_type == 'video':
                await client.send_video(chat_id=message.chat.id, video=file_id)
            elif file_type == 'photo':
                await client.send_photo(chat_id=message.chat.id, photo=file_id)
            elif file_type == 'audio':
                await client.send_audio(chat_id=message.chat.id, audio=file_id)
        else:
            await message.reply_text("Invalid parameter or file not found.")
    else:
        await message.reply_text("Hello! Use the provided link to get your file.")

@app.on_message(filters.command("start"))
async def start(client, message):
    global required_channels
    is_subscribed = await subscription_checker.check(client, message.from_user.id)
    if is_subscribed or not required_channels:
        await start_after_verifying(client, message)
    else:
        buttons = []
        for channel in required_channels:
            button = InlineKeyboardButton(text=f"{channel.lstrip('@')}", url=f"https://t.me/{channel.lstrip('@')}")
            buttons.append([button])
        check_button = InlineKeyboardButton("I've Joined", callback_data="check_subscription")
        reply_markup = InlineKeyboardMarkup(buttons + [[check_button]])
        message_text = ("Hello, welcome to our bot\nPlease join our channel(s) to use the bot and get the latest updates:\n")
        await message.reply(text=message_text, reply_markup=reply_markup)

@app.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query):
    await callback_query.answer()
    is_subscribed = await subscription_checker.check(client, callback_query.from_user.id)
    if is_subscribed:
        await callback_query.message.edit("Thank you for joining!")
        await start_after_verifying(client, callback_query.message)
    else:
        await callback_query.answer("You have not joined the channel yet. Please join and try again.", show_alert=True)

# Command to add files to the database (for admin use)
@app.on_message(filters.command("addfile"))
async def add_file(client, message):
    global DataBaseChannel_id
    if message.chat.id == DataBaseChannel_id:
        if message.reply_to_message:
            file_id = None
            file_type = None
            file_unique_id = None

            if message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id
                file_type = 'document'
                file_unique_id = message.reply_to_message.document.file_unique_id
            elif message.reply_to_message.video:
                file_id = message.reply_to_message.video.file_id
                file_type = 'video'
                file_unique_id = message.reply_to_message.video.file_unique_id
            elif message.reply_to_message.photo:
                file_id = message.reply_to_message.photo.file_id
                file_type = 'photo'
                file_unique_id = message.reply_to_message.photo.file_unique_id
            elif message.reply_to_message.audio:
                file_id = message.reply_to_message.audio.file_id
                file_type = 'audio'
                file_unique_id = message.reply_to_message.audio.file_unique_id

            if file_id and file_type and file_unique_id:
                deep_link = f"{file_type}_{file_unique_id}"
                conn = get_db_connection()
                try:
                    # Check if the file already exists
                    existing_entry = conn.execute('SELECT deep_link FROM files WHERE file_id = ?', (file_id,)).fetchone()
                    if existing_entry:
                        # If the file exists, send the existing deep link
                        bot_user = await client.get_me()
                        await message.reply_text(f"This file is already added. Existing link: https://t.me/{bot_user.username}?start={existing_entry['deep_link']}")
                    else:
                        # If the file does not exist, insert it
                        conn.execute('INSERT INTO files (file_id, file_type, deep_link) VALUES (?, ?, ?)', (file_id, file_type, deep_link))
                        conn.commit()
                        bot_user = await client.get_me()
                        await message.reply_text(f"File added with deep link: https://t.me/{bot_user.username}?start={deep_link}")
                except sqlite3.IntegrityError:
                    bot_user = await client.get_me()
                    await message.reply_text(f"This file is already added. Existing link: https://t.me/{bot_user.username}?start={deep_link}")
                finally:
                    conn.close()
            else:
                await message.reply_text("Unsupported file type.")
        else:
            await message.reply_text("Reply to a document, video, photo, or audio with /addfile to add it.")
    else:
        return None

channels_file = "channels.json"
def save_channels():
    with open(channels_file, "w") as f:
        json.dump(required_channels, f)

# Load required channels from a file
def load_channels():
    global required_channels
    try:
        with open(channels_file, "r") as f:
            required_channels = json.load(f)
    except FileNotFoundError:
        required_channels = []

load_channels()

@app.on_message(filters.command("add_channel") & filters.user(admin_id))
async def add_channel(client, message):
    load_channels()
    channel = message.text.split(" ", 1)[1].strip()
    if channel not in required_channels:
        required_channels.append(channel)
        save_channels()
        await message.reply(f"Channel {channel} added.")
    else:
        await message.reply(f"Channel {channel} is already in the list.")

@app.on_message(filters.command("remove_channel") & filters.user(admin_id))
async def remove_channel(client, message):
    channel = message.text.split(" ", 1)[1].strip()
    if channel in required_channels:
        required_channels.remove(channel)
        save_channels()
        await message.reply(f"Channel {channel} removed.")
    else:
        await message.reply(f"Channel {channel} is not in the list.")

@app.on_message(filters.command("list_channels") & filters.user(admin_id))
async def list_channels(client, message):
    load_channels()
    if required_channels:
        await message.reply("Required channels:\n" + "\n".join(required_channels))
    else:
        await message.reply("No channels in the list.")

users_file = "users.json"
def load_users():
    try:
        with open(users_file, "r") as u:
            return set(json.load(u))  # Load the existing users from the file
    except FileNotFoundError:
        return set()  # Return an empty set if the file does not exist

def save_users(users):
    with open(users_file, "w") as u:
        json.dump(list(users), u)  # Convert the set to a list


# Load the existing users when the bot starts
users = load_users()
@app.on_message(filters.command("send_notice") & filters.user(admin_id))
async def send_notice(client, message):
    load_users()    # Extract the caption and media from the message
    caption = message.caption
    media = message.media

    # Remove the command from the message
    text = message.text
    # print(users)
    # print(caption)
    text = text.strip("/send_notice")
    # print(text)
    # Send the notice to all users who have started the bot
    for user_id in users:
       await app.send_message(text=text,chat_id=user_id)
# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
