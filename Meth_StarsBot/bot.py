import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from threading import Timer

# Load creds from environment
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = Client("methstars", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

# Load balances
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "referrals": {}}

def save():
    with open("data.json", "w") as f:
        json.dump(data, f)

# Meth prices in stars
prices = {
    "0.1g": 1695,
    "0.5g": 4568,
    "1g": 9119,
    "2g": 18238,
    "3.5g": 31920
}
min_required = prices["0.1g"]

# Your Telegram user ID (admin only access)
ADMIN_ID = 5930965838

@app.on_message(filters.command("start"))
def start(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {"stars": 0, "referrals": 0, "muted": False}
        save()
    message.reply("💎 Welcome to MethStars!\nUse /buy 0.1g to cook.\nUse /deposit to learn how to load Stars.")

@app.on_message(filters.command("deposit"))
def deposit(client, message: Message):
    message.reply(f"💳 You need at least {min_required} ⭐️ to start.\nBuy Stars in Telegram, then return to /buy.")

@app.on_message(filters.command("balance"))
def balance(client, message: Message):
    uid = str(message.from_user.id)
    stars = data["users"].get(uid, {}).get("stars", 0)
    message.reply(f"💰 Your balance: {stars} ⭐️ Stars")

@app.on_message(filters.command("addstars") & filters.user(ADMIN_ID))
def addstars(client, message: Message):
    try:
        uid, amt = message.text.split()[1:]
        data["users"].setdefault(uid, {"stars": 0, "referrals": 0, "muted": False})
        data["users"][uid]["stars"] += int(amt)
        save()
        message.reply(f"✅ Added {amt} ⭐️ to {uid}")
    except:
        message.reply("❌ Usage: /addstars <user_id> <amount>")

@app.on_message(filters.command("buy"))
def buy(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2:
        return message.reply("❌ Usage: /buy <amount>\nTry /buy 0.1g or /buy 1g")
    amount = args[1]
    if amount not in prices:
        return message.reply("❌ Invalid amount. Try 0.1g, 1g, etc.")
    if data["users"][uid]["stars"] < min_required:
        return message.reply(f"🚫 You need at least {min_required} ⭐️ to start buying.")
    if data["users"][uid]["stars"] < prices[amount]:
        return message.reply("😓 Not enough Stars. Deposit more to continue.")
    data["users"][uid]["stars"] -= prices[amount]
    save()
    msg = f"✨ {message.from_user.first_name} just bought {amount} of Meth for {prices[amount]} ⭐️!\n📦 Order Confirmed. Stay zooted."
    for u, d in data["users"].items():
        if not d.get("muted"):
            try: app.send_message(int(u), msg)
            except: continue

@app.on_message(filters.command("mute"))
def mute(client, message: Message):
    uid = str(message.from_user.id)
    data["users"][uid]["muted"] = True
    save()
    message.reply("🔕 You’ve muted MethStars ads.")

@app.on_message(filters.command("unmute"))
def unmute(client, message: Message):
    uid = str(message.from_user.id)
    data["users"][uid]["muted"] = False
    save()
    message.reply("🔔 Ads re-enabled. Let the hype flow.")

@app.on_message(filters.command("setup") & filters.user(ADMIN_ID))
def setup_commands(client, message):
    commands = [
        BotCommand("buy", "Buy meth in grams (ex: /buy 0.1g)"),
        BotCommand("balance", "Check your Star balance"),
        BotCommand("deposit", "How to load Stars"),
        BotCommand("mute", "Mute ads"),
        BotCommand("unmute", "Unmute ads")
    ]
    client.set_bot_commands(commands)
    message.reply("✅ Command menu set.")

def broadcast():
    for u, d in data["users"].items():
        if not d.get("muted"):
            try:
                app.send_message(int(u), "📢 Someone just grabbed 1g of Meth! 🚚 /buy 0.1g to get in.")
            except: continue
    Timer(1200, broadcast).start()

broadcast()

if __name__ == "__main__":
    app.run()
