import os
import json
import random
from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from threading import Timer
from datetime import datetime, timedelta

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = Client("methstars", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

# Load database
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "referrals": {}}

def save():
    with open("data.json", "w") as f:
        json.dump(data, f)

prices = {
    "0.1g": 1695,
    "0.5g": 4568,
    "1g": 9119,
    "2g": 18238,
    "3.5g": 31920
}
min_required = prices["0.1g"]
ADMIN_ID = 5930965838

levels = {
    0: "🧪 Rookie",
    10: "💊 Street Runner",
    25: "📦 Dealer",
    50: "👑 Kingpin",
    100: "💎 Meth God"
}

def get_level(xp):
    level_name = "🧪 Rookie"
    for threshold, title in sorted(levels.items()):
        if xp >= threshold:
            level_name = title
    return level_name

@app.on_message(filters.command("start"))
def start(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {"stars": 0, "referrals": 0, "muted": False, "xp": 0, "total_spent": 0, "last_loot": "", "last_xp": ""}
        save()
    message.reply("💎 Welcome to MethStars!\nUse /buy 0.1g to cook.\nUse /deposit to learn how to load Stars.")

@app.on_message(filters.command("deposit"))
def deposit(client, message: Message):
    message.reply(f"💳 You need at least {min_required} ⭐️ to start.\nBuy Stars in Telegram, then return to /buy.")

@app.on_message(filters.command("balance"))
def balance(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].get(uid, {})
    stars = u.get("stars", 0)
    xp = u.get("xp", 0)
    message.reply(f"💰 Stars: {stars} ⭐️\n📈 XP: {xp} ({get_level(xp)})")

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
    data["users"][uid]["xp"] += 1
    data["users"][uid]["total_spent"] += prices[amount]
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
        BotCommand("balance", "Check your Star balance & XP"),
        BotCommand("deposit", "How to load Stars"),
        BotCommand("lootbox", "Claim free meth drop"),
        BotCommand("dice", "Gamble Stars vs the house"),
        BotCommand("top", "Top 5 users by total spent"),
        BotCommand("mute", "Mute ads"),
        BotCommand("unmute", "Unmute ads")
    ]
    client.set_bot_commands(commands)
    message.reply("✅ Command menu set.")

@app.on_message(filters.command("lootbox"))
def lootbox(client, message: Message):
    uid = str(message.from_user.id)
    user = data["users"][uid]
    now = datetime.utcnow().isoformat()
    last = user.get("last_loot", "")
    if last and datetime.fromisoformat(last) > datetime.utcnow() - timedelta(hours=12):
        return message.reply("🎁 You already claimed your lootbox.\nWait 12h for another drop.")
    reward = random.choice(["0.1g", "0.5g", "1g"])
    stars = prices[reward]
    user["stars"] += stars
    user["xp"] += 2
    user["last_loot"] = now
    save()
    message.reply(f"🎁 You opened a lootbox and scored {reward} of Meth!\n💰 +{stars} ⭐️ | 📈 +2 XP")

@app.on_message(filters.command("dice"))
def dice(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return message.reply("🎲 Usage: /dice [amount]")
    amt = int(args[1])
    if data["users"][uid]["stars"] < amt:
        return message.reply("💀 You don't have enough Stars.")
    roll = random.choice(["win", "lose"])
    if roll == "win":
        data["users"][uid]["stars"] += amt
        result = f"✅ You WON! +{amt} ⭐️"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"❌ You lost {amt} ⭐️"
    save()
    message.reply(f"🎲 Rolling the dice...\n{result}")

@app.on_message(filters.command("top"))
def top(client, message: Message):
    leaderboard = sorted(data["users"].items(), key=lambda x: x[1].get("total_spent", 0), reverse=True)[:5]
    lines = ["🏆 Top 5 MethStars users:"]
    for i, (uid, u) in enumerate(leaderboard, 1):
        lines.append(f"{i}. {u.get('username', 'User')} – {u.get('total_spent', 0)} ⭐️ spent")
    message.reply("\n".join(lines))

def give_daily_xp():
    for uid, user in data["users"].items():
        now = datetime.utcnow().isoformat()
        last = user.get("last_xp", "")
        if not last or datetime.fromisoformat(last) < datetime.utcnow() - timedelta(hours=24):
            user["xp"] += 1
            user["last_xp"] = now
    save()
    Timer(3600, give_daily_xp).start()

give_daily_xp()

def broadcast():
    for u, d in data["users"].items():
        if not d.get("muted"):
            try:
                app.send_message(int(u), "📢 Someone just grabbed 1g of Meth! 🚚 /buy 0.1g to join the drip.")
            except: continue
    Timer(1200, broadcast).start()

broadcast()

if __name__ == "__main__":
    app.run()
