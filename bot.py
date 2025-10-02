import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    )

# ─── Load Environment Variables ──────────────────────────────────────────────
load_dotenv()

BOT_NAME = "@safeTextAPIServiceBot"
TOKEN = os.getenv("BOT_TOKEN")
APIKEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT", "https://mogestesema-safe-text-model.hf.space/analyze")

# ─── Logging Setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if not TOKEN or not APIKEY:
    raise ValueError("Missing BOT_TOKEN or API_KEY in environment variables.")

logger.info("✅ Bot initialized successfully")

# ─── Commands ────────────────────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I’m SafeTextAPIServiceBot.\n"
        "Add me to your group and give me admin rights (delete messages) — "
        "I’ll help keep your chat clean and friendly!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡 I detect and delete toxic or harmful messages.\n\n"
        "⚙️ To get started:\n"
        "1️⃣ Add me to your group\n"
        "2️⃣ Grant me admin rights with 'Delete Messages'\n\n"
        "I’ll take care of the rest!"
    )


# ─── Text Analysis ───────────────────────────────────────────────────────────
def analyze_text(text: str) -> dict | None:
    """Send message text to API for toxicity analysis."""
    headers = {"x-api-key": APIKEY}
    payload = {"text": text}

    try:
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.error("⏰ API request timed out.")
    except requests.RequestException as e:
        logger.error(f"🌐 Request error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during API call: {e}")
    return None


# ─── Message Handling ────────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages in groups."""
    message = update.message
    if not message or not message.text:
        return

    user = message.from_user
    chat_type = message.chat.type
    text = message.text.strip()

    logger.info(f"📩 Message from {user.id} in {chat_type}: {text}")

    if chat_type not in ("group", "supergroup"):
        return  # ignore private chats

    # Call external toxicity API
    api_response = analyze_text(text)
    if not api_response:
        logger.warning("⚠️ No response from analysis API.")
        return

    result = api_response.get("result", {})
    avg_score = result.get("average", 0.0)
    toxicity = result.get("toxicity", 0.0)
    obscene = result.get("obscene", 0.0)

    logger.info(
        f"Analyzed '{text[:30]}...' | avg={avg_score:.2f}, toxic={toxicity:.2f}, obscene={obscene:.2f}"
    )

    # Delete messages above threshold
    # Delete messages above threshold
    # Delete messages above threshold
    if avg_score > 20 or toxicity > 50 or obscene > 50:
        try:
            await message.delete()
            username = f"@{user.username}" if user.username else user.first_name or "this user"

            warning_text = (
                f"🚫 Your recent message in {message.chat.title or 'this group'} "
                "was deleted because it contained toxic or inappropriate language.\n\n"
                "⚠️ Please follow community guidelines to keep the chat positive."
            )

            try:
                # Try to send private warning
                await context.bot.send_message(chat_id=user.id, text=warning_text)
                logger.info(f"Sent private warning to {user.id}")
            except Forbidden:
                # Only log if DM fails; optionally send a **very brief notice**
                logger.warning(f"Cannot DM user {user.id}. They might have blocked the bot.")
                # Optional: only send if you really need minimal notice
                # await context.bot.send_message(chat_id=message.chat.id,
                #    text=f"⚠️ A message from {username} was removed.")

            logger.info(f"🧹 Deleted message from {user.id} in chat {message.chat.id}")

        except Forbidden:
            logger.error(
                f"❌ Missing permissions in chat {message.chat.id}. "
                "Please grant 'Delete Messages' admin permission."
            )
        except Exception as e:
            logger.exception(f"Error deleting message: {e}")

# ─── Main Entry ──────────────────────────────────────────────────────────────
def main():
    """Start the bot."""
    logger.info("🚀 Starting SafeTextAPIServiceBot...")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_error_handler(lambda update, context: logger.error(context.error))

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Message handler (non-command text)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot is now polling...")
    app.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()
