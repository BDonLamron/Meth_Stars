# MethStars — Full Meth Casino Experience (Enhanced Fake Activity, UI Buttons)

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import json
import random
import threading
from datetime import datetime, timezone, timedelta

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5930965838

app = Client("methstars", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

if os.path.exists("data.json")):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "orders": [], "feed": [], "lottery": {"entries": [], "last_draw": None}}

def save():
    with open("data.json", "w") as f:
        json.dump(data, f)

# Enhanced Fake AI Feed with Chat, Withdrawals, Viewers
FAKE_USERNAMES = ["@Nter", "@ZootGod", "@MethDealer42", "@GhostCook", "@SkyBuzz"]
FAKE_ACTIONS = [
    lambda: f"🎲 {random.choice(FAKE_USERNAMES)} won {random.randint(200, 3000)} ⭐ on /dice!",
    lambda: f"🎰 {random.choice(FAKE_USERNAMES)} hit a JACKPOT in /slots! +{random.randint(1000, 5000)} ⭐",
    lambda: f"📦 {random.choice(FAKE_USERNAMES)} unboxed 🔥 {random.choice(['💊 0.5g', '👑 1g', '💰 Jackpot'])}",
    lambda: f"🏆 {random.choice(FAKE_USERNAMES)} climbed the leaderboard to #1!",
    lambda: f"🎁 {random.choice(FAKE_USERNAMES)} pulled a mystery prize worth 2000 ⭐",
    lambda: f"📤 {random.choice(FAKE_USERNAMES)} just withdrew 2g Meth to Delacombe VIC 🚚",
    lambda: f"💬 {random.choice(FAKE_USERNAMES)}: This is better than the casino fr 😵‍💫",
    lambda: f"💬 {random.choice(FAKE_USERNAMES)}: just made 10K ⭐ ezpz 🧪",
    lambda: f"👀 {random.randint(7, 19)} users online now..."
]

def fake_feed(client):
    action = random.choice(FAKE_ACTIONS)()
    for uid in data["users"]:
        if random.random() < 0.75:
            try:
                client.send_message(int(uid), action)
            except: pass

def loop_fake_feed():
    fake_feed(app)
    threading.Timer(random.randint(60, 180), loop_fake_feed).start()

# Main menu command
@app.on_message(filters.command("menu"))
def show_menu(client, message: Message):
    animation = "✨✨✨" * 3
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Dice", callback_data="dice"), InlineKeyboardButton("🎰 Slots", callback_data="slots")],
        [InlineKeyboardButton("🎁 Unbox", callback_data="unbox"), InlineKeyboardButton("🎟️ Lotto", callback_data="lotto")],
        [InlineKeyboardButton("📊 Vault", callback_data="vault"), InlineKeyboardButton("🏆 Leaderboard", callback_data="top")],
        [InlineKeyboardButton("📈 Feed", callback_data="feed"), InlineKeyboardButton("🎉 Confetti", callback_data="confetti")],
        [InlineKeyboardButton("🛍️ Shop", callback_data="shop")]
    ])
    client.send_message(message.chat.id, f"{animation}
💊 **Welcome to MethStars** 💊
Choose your vice:
{animation}", reply_markup=keyboard)

@app.on_callback_query()
def handle_buttons(client, cb: CallbackQuery):
    fancy_response = {
        "dice": "🎲 Rolling those dice...",
        "slots": "🎰 Spinning the reels...",
        "unbox": "📦 Cracking open the mystery...",
        "lotto": "🎟️ Entering the Trap Lotto...",
        "vault": "📊 Checking your vault...",
        "top": "🏆 Loading leaderboard...",
        "feed": "📈 Activating AI hype feed...",
        "confetti": "🎉 Dropping confetti bombs!",
        "shop": "🛍️ Loading meth deals..."
    }
    cmd = cb.data
    cb.answer(fancy_response.get(cb.data, "Loading..."))
    client.send_message(cb.message.chat.id, f"/{cmd}")

@app.on_message(filters.command("shop"))
def show_shop(client, message: Message):
    items = [
        {"label": "🧪 0.1g Meth - 200 ⭐", "price": 200, "item": "🧪 0.1g Meth"},
        {"label": "💊 0.5g Meth - 500 ⭐", "price": 500, "item": "💊 0.5g Meth"},
        {"label": "👑 1g Meth - 1000 ⭐", "price": 1000, "item": "👑 1g Meth"}
    ]
    uid = str(message.from_user.id)
    user = data["users"].setdefault(uid, {"stars": 1000, "inventory": []})

    buttons = []
    for i in items:
        buttons.append([InlineKeyboardButton(i["label"], callback_data=f"buy_{i['item']}")])

    client.send_message(
        message.chat.id,
        "🛍️ **MethStars Store** — Spend your ⭐ on exclusive drops:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex("^buy_"))
def buy_item(client, cb: CallbackQuery):
    item_label = cb.data[4:]
    uid = str(cb.from_user.id)
    user = data["users"].setdefault(uid, {"stars": 1000, "inventory": []})
    prices = {"🧪 0.1g Meth": 200, "💊 0.5g Meth": 500, "👑 1g Meth": 1000}

    if item_label not in prices:
        return cb.answer("❌ Item not found")
    if user["stars"] < prices[item_label]:
        return cb.answer("💀 Not enough Stars!", show_alert=True)

    user["stars"] -= prices[item_label]
    user["inventory"].append(item_label)
    save()
    cb.answer("✅ Purchased!")
    client.send_message(cb.message.chat.id, f"📦 You bought: {item_label}")

# Enhanced slot animation
@app.on_message(filters.command("slots"))
def slots_game(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].setdefault(uid, {"stars": 1000})
    try:
        amt = int(message.text.split()[1])
        if amt <= 0 or u["stars"] < amt:
            return message.reply("❌ Not enough Stars!")
        client.send_message(message.chat.id, "🎰 Spinning...")
        threading.Timer(2.0, lambda: resolve_slots(client, message, amt)).start()
    except:
        message.reply("Usage: /slots [amount]")

def resolve_slots(client, message, amt):
    uid = str(message.from_user.id)
    u = data["users"][uid]
    spin = [random.choice(["🍒", "💎", "7️⃣"]) for _ in range(3)]
    win = spin.count(spin[0]) == 3
    if win:
        reward = amt * 3
        u["stars"] += reward
        result = f"{''.join(spin)}
🎉 JACKPOT! +{reward} ⭐"
    else:
        u["stars"] -= amt
        result = f"{''.join(spin)}
😢 You lost {amt} ⭐"
    save()
    client.send_message(message.chat.id, result)

# Enhanced unbox animation
@app.on_message(filters.command("unbox"))
def enhanced_unbox(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].setdefault(uid, {"stars": 1000, "inventory": [], "xp": 0})
    if u["stars"] < 500:
        return message.reply("💀 Not enough Stars! Mystery Box costs 500 ⭐")
    u["stars"] -= 500
    client.send_message(message.chat.id, "📦 Cracking open your box...")
    threading.Timer(2.0, lambda: finish_unbox(client, message)).start()

def finish_unbox(client, message):
    uid = str(message.from_user.id)
    u = data["users"][uid]
    rewards = ["🧪 0.1g Meth", "💊 0.5g Meth", "👑 1g Meth", "⭐ 1000", "💰 Jackpot 5000 ⭐"]
    prize = random.choice(rewards)
    u["inventory"].append(prize)
    u["xp"] += 50
    save()
    client.send_message(message.chat.id, f"🎁 BOOM! You won: {prize} 🎉")

# Start enhanced loop
loop_fake_feed()
run_lottery()
