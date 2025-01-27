import openai
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Tokens
TELEGRAM_TOKEN = "8179478525:AAFx1_094x1EWYTcVfBGOWuHsaXqMQ6B4CQ"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Load knowledge base
KNOWLEDGE_BASE_FILE = "knowledge_base.json"

def load_knowledge_base():
    try:
        with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

knowledge_base = load_knowledge_base()

# Save knowledge base
def save_knowledge_base():
    with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as file:
        json.dump(knowledge_base, file, ensure_ascii=False, indent=4)

# Add new knowledge (Admin only)
def add_knowledge(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    admin_id = 123456789  # Replace with your Telegram user ID
    if user_id != admin_id:
        update.message.reply_text("You are not authorized to add knowledge.")
        return

    try:
        title, content = " ".join(context.args).split("|", 1)
        knowledge_base[title.strip()] = content.strip()
        save_knowledge_base()
        update.message.reply_text(f"Knowledge added: {title.strip()}")
    except ValueError:
        update.message.reply_text("Invalid format. Use: /add title | content")

# Search knowledge base
def search_knowledge_base(query):
    for title, content in knowledge_base.items():
        if query.lower() in title.lower():
            return content
    return None

# Handle messages
def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    response = search_knowledge_base(query)

    if response:
        update.message.reply_text(response)
    else:
        # Fallback to OpenAI
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": query}]
            )
            reply = completion.choices[0].message['content']
            update.message.reply_text(reply)
        except Exception as e:
            update.message.reply_text("Error communicating with OpenAI: " + str(e))

# Main function
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("add", add_knowledge))

    # Message handling
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
