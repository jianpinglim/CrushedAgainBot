import os
import sqlite3
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from time import time
from functools import wraps

# Redeploy fix for Procfile
# Load environment variables
load_dotenv()

# Database setup
conn = sqlite3.connect("crushbot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS Users (user_id INTEGER PRIMARY KEY, username TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS Crushes (user_id INTEGER PRIMARY KEY, crush_user_id INTEGER)")
conn.commit()

# Bot setup
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("You must set the BOT_TOKEN environment variable")
try:
    application = Application.builder().token(BOT_TOKEN).build()
except Exception as e:
    print(f"Failed to initialize bot: {e}")
    exit(1)

# Rate limiting setup
RATE_LIMIT = 7  # seconds
last_command_time = {}

def rate_limit(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        current_time = time()
        if user_id in last_command_time:
            elapsed_time = current_time - last_command_time[user_id]
            if elapsed_time < RATE_LIMIT:
                remaining = int(RATE_LIMIT - elapsed_time)
                await update.message.reply_text(f"Please wait {remaining} second{'s' if remaining != 1 else ''} before using this command again.")
                return
        last_command_time[user_id] = current_time
        return await func(update, context, *args, **kwargs)
    return wrapped

@rate_limit
async def start(update, context):
    user_id = update.effective_user.id
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text("You must set a Telegram username in Settings to use this bot.")
        return
    try:
        cursor.execute("INSERT OR REPLACE INTO Users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        await update.message.reply_text(
            "Welcome to CrushMatcher! 😊\n"
            "Commands:\n/start - Begin\n/setcrush @username - Set your crush\n/clearcrush - Reset your crush\n/help - Learn more about Crushed"
        )
    except sqlite3.Error as e:
        await update.message.reply_text("Oops, something went wrong. Try again later!")
        print(f"Database error in start: {e}")

@rate_limit
async def setcrush(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if not username:
        await update.message.reply_text("You must set a Telegram username in Settings to use this bot.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setcrush @username")
        return
    crush_username_input = context.args[0].lstrip("@")
    
    try:
        # Update user's username
        cursor.execute("INSERT OR REPLACE INTO Users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

        # Find crush's user_id
        cursor.execute("SELECT user_id, username FROM Users WHERE LOWER(username) = LOWER(?)", (crush_username_input,))
        result = cursor.fetchone()
        if not result:
            await update.message.reply_text("Don’t be disheartened! Your crush hasn’t started the bot yet. Get them to try it!")
            return
        crush_user_id, crush_username = result

        if crush_user_id == user_id:
            await update.message.reply_text("You can’t set yourself as your crush, weirdo! LOL JK 😜")
            return
        
        # Set crush
        cursor.execute("INSERT OR REPLACE INTO Crushes (user_id, crush_user_id) VALUES (?, ?)", (user_id, crush_user_id))
        conn.commit()

        # Check for mutual crush
        cursor.execute("SELECT crush_user_id FROM Crushes WHERE user_id = ?", (crush_user_id,))
        result = cursor.fetchone()
        if result and result[0] == user_id:
            await context.bot.send_message(chat_id=user_id, text=f"Congratulations! @{crush_username} likes you back! 😍")
            await context.bot.send_message(chat_id=crush_user_id, text=f"🎉 It’s a match! You and @{username} both have a crush on each other! 🎉")
        else:
            await update.message.reply_text(f"Successfully set crush to @{crush_username}! 😊")
    except sqlite3.Error as e:
        await update.message.reply_text("Oops, something went wrong. Try again later!")
        print(f"Database error in setcrush: {e}")

@rate_limit
async def help(update, context):
    await update.message.reply_text(
        "📱 *Crushed Help Guide* 📱\n\n"
        "*What is Crushed?*\n"
        "Crushed is a private, discreet way to discover if someone likes you back! NO MORE FEAR OF REJECTION!!\n\n"
        "*How It Works:*\n"
        "1️⃣ Start the bot with /start\n"
        "2️⃣ Set your crush with /setcrush @username\n"
        "3️⃣ If they've also set you as their crush, you'll both be notified! 🎉\n\n"
        "*Commands:*\n"
        "• /start - Initialize the bot\n"
        "• /setcrush @username - Set who you have a crush on\n"
        "• /clearcrush - Remove your current crush\n"
        "• /help - Show this help message\n\n"
        "*Privacy:*\n"
        "• Your crush is completely private unless it's mutual\n"
        "• No one will know who you like unless they like you back\n\n"
        "*Tips:*\n"
        "• Make sure your crush has also used this bot\n"
        "• Be patient - they might not have set their crush yet\n"
        "• Share this bot with your friends to increase your chances!",
        parse_mode="Markdown"
    )

# Add the help command handler under your other handlers
application.add_handler(CommandHandler("help", help))

@rate_limit
async def clearcrush(update, context):
    user_id = update.message.from_user.id
    try:
        cursor.execute("DELETE FROM Crushes WHERE user_id = ?", (user_id,))
        conn.commit()
        await update.message.reply_text("Successfully cleared crush! Wishing you all the best! 😢")
    except sqlite3.Error as e:
        await update.message.reply_text("Oops, something went wrong. Try again later!")
        print(f"Database error in clearcrush: {e}")

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("setcrush", setcrush))
application.add_handler(CommandHandler("clearcrush", clearcrush))

# Start the bot
print("Bot is starting...")
application.run_polling()
conn.close()  # Clean up database connection when bot stops