import os
import threading
from flask import Flask
from bot import main  # import your main function from bot.py

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Safe Text API Bot is running on Render!"

# Run your Telegram bot in a background thread
threading.Thread(target=main, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
