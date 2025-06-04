import requests from telegram import Update, ForceReply from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler import re

Telegram Bot Token

BOT_TOKEN = "8028110075:AAEF5EctyqFimN4v3YwO8lG7cNHv6LFsg1Y"

Render Deployment API Endpoint

DEPLOYMENT_API = "https://sarkar-md-free.onrender.com/deploy"

Stages for conversation

GITHUB, SESSION = range(2)

Simple in-memory storage

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "👋 Welcome to the Arslan-MD Bot Deployer!\n\n" "To get started, please send your forked GitHub repo link of Sarkar-MD:\n" "(It must be forked from https://github.com/Sarkar-Bandaheali/Sarkar-MD)" ) return GITHUB

async def validate_github(update: Update, context: ContextTypes.DEFAULT_TYPE): github_url = update.message.text.strip() username_match = re.match(r"https://github.com/([\w-]+)/Sarkar-MD", github_url)

if not username_match:
    await update.message.reply_text("❌ Invalid GitHub repo link. Make sure it's a fork of Sarkar-MD.")
    return GITHUB

username = username_match.group(1)
user_data[update.effective_user.id] = {"github": github_url, "username": username}

await update.message.reply_text("✅ GitHub link validated! Now please send your WhatsApp Session ID:")
return SESSION

async def receive_session(update: Update, context: ContextTypes.DEFAULT_TYPE): session_id = update.message.text.strip() data = user_data.get(update.effective_user.id)

if not data:
    await update.message.reply_text("⚠️ Session expired. Please start again with /start.")
    return ConversationHandler.END

payload = {
    "username": data["username"],
    "repo_url": data["github"],
    "session": session_id
}

await update.message.reply_text("🚀 Deploying your bot... Please wait...")
try:
    response = requests.post(DEPLOYMENT_API, json=payload)
    if response.status_code == 200:
        await update.message.reply_text("✅ Bot Deployed Successfully! 🎉\nCheck your Render dashboard.")
    else:
        await update.message.reply_text(f"❌ Deployment failed. Server response: {response.text}")
except Exception as e:
    await update.message.reply_text(f"❌ Error: {str(e)}")

return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("❌ Cancelled.") return ConversationHandler.END

def main(): app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GITHUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_github)],
        SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_session)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv_handler)
app.run_polling()

if name == 'main': main()

