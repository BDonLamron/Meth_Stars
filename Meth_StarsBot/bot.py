import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from threading import Timer

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = Client("methstars", bot_token=TOKEN)

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

# Minimum to unlock store
min_required = prices["0.1g"]

@app.on_message(filters.command("start"))
def start(client, message: Message):
    user_id = str(message.from_user.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"stars": 0, "referrals": 0, "muted": False}
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

@app.on_message(filters.command("addstars") & filters.user([5930965838]))
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

# Background broadcast every 20 minutes
def broadcast():
    for u, d in data["users"].items():
        if not d.get("muted"):
            try:
                app.send_message(int(u), "📢 Someone just bought 1g of Meth! 🔥 Type /buy 0.1g to start.")
            except: continue
    Timer(1200, broadcast).start()

broadcast()

if __name__ == "__main__":
    app.run()
