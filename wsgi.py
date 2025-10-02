import requests, threading, time, os
from flask import Flask
from bot import main  # import your main function from bot.py

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Safe Text API Bot is running on Render!"

def self_ping():
    url = "https://safe-text-telegram-bot-1.onrender.com"
    if not url:
        return
    while True:
        try:
            requests.get(url)
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(600) 

# Run your Telegram bot in a background thread
threading.Thread(target=main, daemon=True).start()
threading.Thread(target=self_ping,daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
