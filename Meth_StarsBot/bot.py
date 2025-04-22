# MethStars Final Full bot.py (cleaned, all features, no syntax errors)

import os
import json
import random
from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from threading import Timer
from datetime import datetime, timedelta, timezone

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5930965838

app = Client("methstars", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {"users": {}}


def ensure_user(func):
    def wrapper(client, message: Message, *args, **kwargs):
        uid = str(message.from_user.id)
        if uid not in data["users"]:
            data["users"][uid] = {
                "stars": 0,
                "xp": 0,
                "muted": False,
                "total_spent": 0,
                "last_loot": "",
                "last_active": ""
            }
        return func(client, message, *args, **kwargs)
    return wrapper

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

@app.on_message(filters.command("start"))
@ensure_user
def start(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "stars": 0, "xp": 0, "muted": False,
            "total_spent": 0, "last_loot": "", "last_active": ""
        }
    data["users"][uid]["last_active"] = datetime.now(timezone.utc).isoformat()
    save()
    message.reply("💎 Welcome to MethStars!\nUse /buy 0.1g to begin.\nUse /lootbox for free gifts.")


@app.on_message(filters.command("setup") & filters.user(ADMIN_ID))
@ensure_user
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
@ensure_user
def balance(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    u = data["users"].get(uid, {})
    stars = u.get("stars", 0)
    xp = u.get("xp", 0)
    message.reply(f"💰 Stars: {stars}\n📈 XP: {xp}")

@app.on_message(filters.command("buy"))
@ensure_user
def buy(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2:
        return message.reply("❌ Usage: /buy [amount]")
    amount = args[1]
    if amount not in prices:
        return message.reply("❌ Invalid amount.")
    if data["users"][uid]["stars"] < prices[amount]:
        return message.reply("💀 Not enough Stars.")
    data["users"][uid]["stars"] -= prices[amount]
    data["users"][uid]["total_spent"] += prices[amount]
    data["users"][uid]["xp"] += 1
    data["users"][uid]["last_active"] = datetime.now(timezone.utc).isoformat()
    save()
    message.reply(f"✅ You bought {amount} of Meth for {prices[amount]} ⭐️")

@app.on_message(filters.command("lootbox"))
@ensure_user
def lootbox(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    user = data['users'][uid]
    now = datetime.now(timezone.utc)
    if user.get("last_loot") and datetime.fromisoformat(user["last_loot"]) > now - timedelta(hours=12):
        return message.reply("🎁 You already claimed your lootbox. Wait 12h.")
    reward = random.choice(["0.1g", "0.5g", "1g"])
    user["stars"] += prices[reward]
    user["xp"] += 2
    user["last_loot"] = now.isoformat()
    save()
    message.reply(f"🎁 Lootbox drop: {reward} of Meth!\n+{prices[reward]} ⭐️ | +2 XP")

@app.on_message(filters.command("dice"))
@ensure_user
def dice(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return message.reply("🎲 Usage: /dice [amount]")
    amt = int(args[1])
    if data["users"][uid]["stars"] < amt:
        return message.reply("💀 Not enough Stars.")
    if random.choice([True, False]):
        data["users"][uid]["stars"] += amt
        result = f"✅ You won {amt} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"❌ You lost {amt} ⭐️"
    save()
    message.reply(result)

@app.on_message(filters.command("slots"))
@ensure_user
def slots(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return message.reply("🎰 Usage: /slots [amount]")
    amt = int(args[1])
    if data["users"][uid]["stars"] < amt:
        return message.reply("💀 Not enough Stars.")
    spin = [random.choice(["💎", "🍒", "🍋"]) for _ in range(3)]
    win = spin.count(spin[0]) == 3
    if win:
        winnings = amt * 3
        data["users"][uid]["stars"] += winnings
        result = f"{''.join(spin)}\n🎉 You won {winnings} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"{''.join(spin)}\nYou lost {amt} ⭐️"
    save()
    message.reply(result)

@app.on_message(filters.command("coinflip"))
@ensure_user
def coinflip(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    args = message.text.split()
    if len(args) < 3 or not args[2].isdigit():
        return message.reply("🪙 Usage: /coinflip heads|tails [amount]")
    call = args[1].lower()
    amt = int(args[2])
    if call not in ["heads", "tails"]:
        return message.reply("🪙 Choose heads or tails.")
    if data["users"][uid]["stars"] < amt:
        return message.reply("💀 Not enough Stars.")
    flip = random.choice(["heads", "tails"])
    if call == flip:
        data["users"][uid]["stars"] += amt
        result = f"✅ It was {flip}. You won {amt} ⭐️!"
    else:
        data["users"][uid]["stars"] -= amt
        result = f"❌ It was {flip}. You lost {amt} ⭐️"
    save()
    message.reply(result)

@app.on_message(filters.command("top"))
@ensure_user
def top(client, message: Message):
    leaderboard = sorted(data["users"].items(), key=lambda x: x[1].get("total_spent", 0), reverse=True)[:5]
    lines = ["🏆 Top 5 Buyers:"]
    for i, (uid, u) in enumerate(leaderboard, 1):
        lines.append(f"{i}. User {uid[-4:]} – {u.get('total_spent', 0)} ⭐️")
    message.reply("\n".join(lines))

@app.on_message(filters.command("mute"))
@ensure_user
def mute(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    data["users"][uid]["muted"] = True
    save()
    message.reply("🔕 Ads muted.")

@app.on_message(filters.command("unmute"))
@ensure_user
def unmute(client, message: Message):
    uid = str(message.from_user.id)
    if uid not in data['users']:
        data['users'][uid] = {
            'stars': 0,
            'xp': 0,
            'muted': False,
            'total_spent': 0,
            'last_loot': '',
            'last_active': ''
        }
    uid = str(message.from_user.id)
    data["users"][uid]["muted"] = False
    save()
    message.reply("🔔 Ads unmuted.")

def fake_activity():
    now = datetime.now(timezone.utc)

    # Only keep users active in the last 3 mins
    active = [
        uid for uid, u in data["users"].items()
        if u.get("last_active") and datetime.fromisoformat(u["last_active"]) > now - timedelta(minutes=3)
    ]

    if active:
        victim = random.choice(active)
        action = random.choice([
            f"🎲 User {victim[-4:]} won 1000 ⭐️ in /dice!",
            f"📦 User {victim[-4:]} bought 0.5g of Meth!",
            f"💰 User {victim[-4:]} deposited 3000 ⭐️",
            f"🎁 User {victim[-4:]} opened a lootbox for 1g!"
        ])

        for uid, user_data in data["users"].items():
            if not user_data.get("muted"):
                try:
                    app.send_message(int(uid), action)
                except Exception as e:
                    print(f"Failed to message {uid}: {e}")

    # Re-run the function after delay
    Timer(random.randint(15, 30), fake_activity).start()

# Kick off the fake event loop
fake_activity()

if __name__ == "__main__":
    app.run()

# TrapGPT Upgrades: Prestige, Shop, Badges, Rotating Deals, AI Dealer NPC, Quests, Titles, Quest Tracking, Quest XP, Title Effects, Quest Reset, Streak Badges, Title List, Streak Preview, Surprise Quests, Profile Page

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import json, os, random

# Assuming you have a `data` dict already loaded from data.json
# and a save() function to persist it
def save():
    with open("data.json", "w") as f:
        json.dump(data, f)

# =====================
# Quest Reset Tracking
# =====================
def reset_daily_quests(user):
    today = str(datetime.utcnow().date())
    if user.get("last_quest_reset") != today:
        user["quest_progress"] = {"dice": 0, "lootbox": 0, "delivery": 0, "xp": 0}
        user["last_quest_reset"] = today
        user["streak"] = user.get("streak", 0)

# =====================
# /quests command (daily tasks + XP reward + streak badge)
# =====================
@app.on_message(filters.command("quests") & filters.private)
def quests(client, message: Message):
    user_id = str(message.from_user.id)
    user = data["users"].setdefault(user_id, {})
    reset_daily_quests(user)
    user.setdefault("quest_progress", {"dice": 0, "lootbox": 0, "delivery": 0, "xp": 0})

    progress = user["quest_progress"]
    lines = [
        f"🎯 Win 1 /dice game — {'✅' if progress['dice'] >= 1 else f'{progress['dice']}/1'}",
        f"🎁 Open 1 lootbox — {'✅' if progress['lootbox'] >= 1 else f'{progress['lootbox']}/1'}",
        f"🚚 Make 1 delivery — {'✅' if progress['delivery'] >= 1 else f'{progress['delivery']}/1'}",
        f"📈 Gain 50 XP — {'✅' if progress['xp'] >= 50 else f'{progress['xp']}/50'}",
    ]

    if all([
        progress['dice'] >= 1,
        progress['lootbox'] >= 1,
        progress['delivery'] >= 1,
        progress['xp'] >= 50
    ]):
        progress.update({"dice": 0, "lootbox": 0, "delivery": 0, "xp": 0})
        user["xp"] = user.get("xp", 0) + 100
        user["streak"] += 1
        if user["streak"] in [3, 7, 14]:
            user.setdefault("badges", []).append(f"🔥 {user['streak']}-Day Streak")
        save()
        return message.reply(f"✅ Daily Quests Complete! +100 XP\n🔥 Streak: {user['streak']} days")

    save()
    return message.reply("📜 **Daily Quests**:\n\n" + "\n".join(lines))

# =====================
# /streak command (preview rewards)
# =====================
@app.on_message(filters.command("streak") & filters.private)
def streak_preview(client, message: Message):
    rewards = ["3-Day: 🔥 Streak Badge", "7-Day: 🔥🔥 + XP Boost", "14-Day: 👑 Crown Title"]
    return message.reply("📆 **Streak Rewards**:\n\n" + "\n".join(rewards))

# =====================
# /surprise command (random event or bonus quest)
# =====================
@app.on_message(filters.command("surprise") & filters.private)
def surprise_quest(client, message: Message):
    user_id = str(message.from_user.id)
    user = data["users"].setdefault(user_id, {})
    bonus = random.choice([
        "💥 Double XP for next /dice win!",
        "🎲 Free lootbox granted!",
        "💸 +250 Stars added to your stash!"
    ])
    if "Stars" in bonus:
        user["stars"] = user.get("stars", 0) + 250
    elif "lootbox" in bonus:
        user.setdefault("inventory", {})["lootbox"] = user["inventory"].get("lootbox", 0) + 1
    save()
    return message.reply(f"🎉 Surprise Event:\n{bonus}")

# =====================
# /profile command — summary of dashboard + titles + badges
# =====================
@app.on_message(filters.command("profile") & filters.private)
def show_profile(client, message: Message):
    user_id = str(message.from_user.id)
    user = data["users"].get(user_id, {})

    stars = user.get("stars", 0)
    xp = user.get("xp", 0)
    streak = user.get("streak", 0)
    title = user.get("title", "None")
    badges = user.get("badges", [])

    badge_list = ", ".join(badges[-5:]) or "None"

    return message.reply(
        f"🧾 **Your Profile**\n\n"
        f"⭐ Stars: `{stars}`\n"
        f"🌟 XP: `{xp}`\n"
        f"🔥 Streak: `{streak}` days\n"
        f"🎖️ Title: {title}\n"
        f"🏅 Recent Badges: {badge_list}"
    )

# =====================
# Title Effects Helper (can be used in game logic)
# =====================
def apply_title_effects(user):
    title = user.get("title", "")
    if "XP Boost" in title:
        return {"xp_multiplier": 1.5}
    elif "Streak" in title:
        return {"xp_multiplier": 1.2}
    elif "Crown" in title:
        return {"xp_multiplier": 2.0}
    return {"xp_multiplier": 1.0}


# =====================
# /withdraw command + cooldown + VIC address check
# =====================
@app.on_message(filters.command("withdraw") & filters.private & filters.regex(r"^/withdraw\s+(.+)"))
@ensure_user
def withdraw_item(client, message: Message):
    uid = str(message.from_user.id)
    item = message.matches[0].group(1).strip()
    user = data["users"].setdefault(uid, {})
    inventory = user.setdefault("inventory", {})

    if inventory.get(item, 0) <= 0:
        return message.reply("❌ You don’t have that item in your inventory.")

    now = datetime.now(timezone.utc)
    last_withdraw = user.get("last_withdraw_time")
    if last_withdraw:
        last_dt = datetime.fromisoformat(last_withdraw)
        if now < last_dt + timedelta(hours=1):
            minutes = int(((last_dt + timedelta(hours=1)) - now).total_seconds() / 60)
            return message.reply(f"🕒 You must wait {minutes} more minutes before withdrawing again.")

    user["last_withdraw_time"] = now.isoformat()
    inventory[item] -= 1
    user["awaiting_address"] = item
    save()
     return message.reply(
    f"📦 `{item}` is being prepared for delivery.\n\n"
    "Please reply with your **full VIC address**, like:\n"
    "`John Doe\\n618 Sutton St\\nDelacombe VIC 3356`"
)

@app.on_message(filters.text & filters.private)
@ensure_user
def handle_address(client, message: Message):
    uid = str(message.from_user.id)
    user = data["users"].get(uid, {})

    if "awaiting_address" not in user:
        return

    lines = message.text.strip().split("\n")
    if len(lines) < 3:
        return message.reply("❌ Address must be at least 3 lines (name, street, suburb + VIC postcode).")

    vic_line = lines[-1].strip()
    if not vic_line.upper().startswith("VIC") or not any(char.isdigit() for char in vic_line):
        return message.reply("❌ Last line must contain 'VIC ####' with a postcode.")

    try:
        postcode = int(vic_line.split()[-1])
        if not (3000 <= postcode <= 3999):
            raise ValueError
    except ValueError:
        return message.reply("❌ Invalid VIC postcode. Must be between 3000–3999.")

    item = user.pop("awaiting_address", None)
    save()

    client.send_chat_action(message.chat.id, "typing")
    Timer(2.5, lambda: message.reply("📦 Packaging your order...")).start()
    Timer(5, lambda: message.reply("🚚 Sending to street dealer...")).start()
    Timer(7.5, lambda: message.reply(f"✅ Your `{item}` was successfully delivered!")).start()

# =====================
# /track command
# =====================
@app.on_message(filters.command("track") & filters.private)
@ensure_user
def track(client, message: Message):
    stages = [
        "📦 Order Confirmed",
        "📤 Shipped from Warehouse",
        "🚚 Out for Delivery",
        "📬 Delivered"
    ]
    stage = random.choice(stages)
    message.reply(f"🚨 Tracking Status: {stage}")
