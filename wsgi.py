import os
import time
import threading
import requests
from flask import Flask
from bot import main  # import your main function from bot.py

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Safe Text API Bot is running on Render!"

# ✅ Background self-ping to keep service awake
def self_ping():
    url = "https://safe-text-telegram-bot-1.onrender.com"  # replace with your Render URL
    if not url:
        return
    while True:
        try:
            requests.get(url)
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(600)  # every 10 minutes

# ✅ Safe delayed bot start (prevents Telegram 409 conflict)
def start_bot_safely():
    time.sleep(5)  # wait a few seconds to let Flask start
    main()  # run your bot's main polling loop

# ✅ Start both background threads
threading.Thread(target=start_bot_safely, daemon=True).start()
threading.Thread(target=self_ping, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
