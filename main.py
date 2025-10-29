import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

# Load tokens from environment
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Clean up Telegram token if it has "HTTP API: " prefix
if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN.startswith('HTTP API: '):
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN.replace('HTTP API: ', '').strip()

# Initialize OpenAI client
# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
openai = OpenAI(api_key=OPENAI_API_KEY)

# Merry Harper's personality - you can customize this!
SYSTEM_PROMPT = """You are Merry Harper, a friendly and caring AI friend. You chat like a real person would text - warm, genuine, and supportive. Keep your responses natural and conversational, like you're texting a close friend."""

# Store conversation history for each user (last 10 messages)
conversation_memory = {}
MAX_MESSAGES = 10


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    await update.message.reply_text(
        f"Hey {update.effective_user.first_name}! I'm Merry Harper. "
        "Let's chat! 😊"
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    user_id = update.effective_user.id
    conversation_memory[user_id] = []
    await update.message.reply_text("Conversation cleared! Starting fresh. ✨")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and respond using OpenAI"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation memory for new users
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    # Add user message to history
    conversation_memory[user_id].append({"role": "user", "content": user_message})
    
    # Build messages for OpenAI with system prompt
    # Only send the last MAX_MESSAGES exchanges (last 20 entries)
    recent_history = conversation_memory[user_id][-(MAX_MESSAGES * 2):]
    
    # Ensure the first message is always from the user (not assistant)
    if recent_history and recent_history[0].get("role") == "assistant":
        recent_history = recent_history[1:]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + recent_history
    
    try:
        # Get response from OpenAI
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=messages,
        )
        bot_reply = response.choices[0].message.content
        
        # Save bot's response to memory
        conversation_memory[user_id].append({"role": "assistant", "content": bot_reply})
        
        # Trim conversation to keep only last MAX_MESSAGES exchanges (user + assistant pairs)
        if len(conversation_memory[user_id]) > MAX_MESSAGES * 2:
            conversation_memory[user_id] = conversation_memory[user_id][-(MAX_MESSAGES * 2):]
        
        # Send reply to user
        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        # Log the error and send a friendly message to the user
        print(f"OpenAI API error: {e}")
        await update.message.reply_text(
            "Sorry, I'm having trouble thinking right now. Can you try again? 🤔"
        )


def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY")
        return
    
    # Start keep-alive server for 24/7 uptime
    keep_alive()
    
    # Create bot application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Merry Harper is online")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
