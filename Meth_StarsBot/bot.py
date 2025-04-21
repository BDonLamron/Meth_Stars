

# -- START OF SCRIPT --

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

# Load balances
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {"users": {}}

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

@app.on_message(filters.command("start"))
def start(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "stars": 0, "xp": 0, "muted": False,
            "total_spent": 0, "last_loot": "", "last_active": ""
        }
    else:
        data["users"][uid]["last_active"] = datetime.utcnow().isoformat()
    save()
    message.reply("💎 Welcome to MethStars!
Use /buy 0.1g to begin.
Use /lootbox for free gifts.")

@app.on_message(filters.command("setup") & filters.user(ADMIN_ID))
def setup(client, message):
    commands = [
        BotCommand("buy", "Buy meth in grams"),
        BotCommand("balance", "View balance and XP"),
        BotCommand("lootbox", "Claim free meth drop"),
        BotCommand("dice", "Gamble your Stars"),
        BotCommand("slots", "Slot machine"),
        BotCommand("coinflip", "Heads or tails?"),
        BotCommand("top", "Leaderboard"),
        BotCommand("mute", "Mute bot ads"),
        BotCommand("unmute", "Unmute ads"),
    ]
    client.set_bot_commands(commands)
    message.reply("✅ Menu setup complete.")

@app.on_message(filters.command("balance"))
def balance(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].get(uid, {})
    stars = u.get("stars", 0)
    xp = u.get("xp", 0)
    message.reply(f"💰 Stars: {stars}
📈 XP: {xp}")

@app.on_message(filters.command("buy"))
def buy(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2: return message.reply("Usage: /buy [amount]")
    amount = args[1]
    if amount not in prices: return message.reply("Invalid option.")
    if data["users"][uid]["stars"] < prices[amount]: return message.reply("Insufficient Stars.")
    data["users"][uid]["stars"] -= prices[amount]
    data["users"][uid]["total_spent"] += prices[amount]
    data["users"][uid]["xp"] += 1
    data["users"][uid]["last_active"] = datetime.utcnow().isoformat()
    save()
    for u, d in data["users"].items():
        if not d.get("muted"):
            try:
                app.send_message(int(u), f"📦 @{message.from_user.username or uid} bought {amount} Meth!")
            except: continue

@app.on_message(filters.command("lootbox"))
def lootbox(client, message: Message):
    uid = str(message.from_user.id)
    user = data["users"][uid]
    now = datetime.utcnow()
    if user.get("last_loot") and datetime.fromisoformat(user["last_loot"]) > now - timedelta(hours=12):
        return message.reply("🎁 Come back later. Cooldown: 12h")
    reward = random.choice(["0.1g", "0.5g", "1g"])
    data["users"][uid]["stars"] += prices[reward]
    data["users"][uid]["xp"] += 2
    data["users"][uid]["last_loot"] = now.isoformat()
    save()
    message.reply(f"🎁 Lootbox: You received {reward} Meth!")

@app.on_message(filters.command("dice"))
def dice(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit(): return message.reply("Usage: /dice [amount]")
    amt = int(args[1])
    if data["users"][uid]["stars"] < amt: return message.reply("Too broke.")
    win = random.choice([True, False])
    if win:
        data["users"][uid]["stars"] += amt
        result = f"You won {amt} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"You lost {amt} ⭐️"
    save()
    message.reply(result)

@app.on_message(filters.command("slots"))
def slots(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit(): return message.reply("Usage: /slots [amount]")
    amt = int(args[1])
    if data["users"][uid]["stars"] < amt: return message.reply("Not enough Stars.")
    symbols = ["💎", "🍒", "🍋"]
    spin = [random.choice(symbols) for _ in range(3)]
    match = spin.count(spin[0]) == 3
    if match:
        win = amt * 3
        data["users"][uid]["stars"] += win
        result = f"{''.join(spin)}
🎉 You won {win} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"{''.join(spin)}
You lost {amt} ⭐️"
    save()
    message.reply(result)

@app.on_message(filters.command("coinflip"))
def coinflip(client, message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 3 or not args[2].isdigit(): return message.reply("Usage: /coinflip heads|tails amount")
    guess = args[1]
    amt = int(args[2])
    flip = random.choice(["heads", "tails"])
    if guess == flip:
        data["users"][uid]["stars"] += amt
        msg = f"🪙 It's {flip}! You won {amt} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        msg = f"🪙 It's {flip}. You lost {amt} ⭐️"
    save()
    message.reply(msg)

@app.on_message(filters.command("top"))
def top(client, message: Message):
    leaderboard = sorted(data["users"].items(), key=lambda x: x[1].get("total_spent", 0), reverse=True)[:5]
    msg = "🏆 Top 5:
"
    for i, (uid, u) in enumerate(leaderboard, 1):
        msg += f"{i}. @{u.get('username', uid)} - {u.get('total_spent', 0)} ⭐️
"
    message.reply(msg)

def fake_activity():
    active = [uid for uid, u in data["users"].items()
              if u.get("last_active") and datetime.fromisoformat(u["last_active"]) > datetime.utcnow() - timedelta(minutes=3)]
    if active:
        victim = random.choice(active)
        actions = [
            f"🎲 @{victim} just won 1000 ⭐️ in /dice!",
            f"📦 @{victim} bought 0.5g Meth!",
            f"💰 @{victim} deposited 3000 ⭐️",
            f"🎁 @{victim} scored 1g from a lootbox!"
        ]
        try:
            for u in data["users"]:
                if not data["users"][u].get("muted"):
                    app.send_message(int(u), random.choice(actions))
        except:
            pass
    Timer(random.randint(15, 30), fake_activity).start()

fake_activity()

# -- END OF SCRIPT --
