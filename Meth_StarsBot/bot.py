# MethStars — Full Meth Casino Experience (Enhanced Fake Activity, UI Buttons)

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import json
import random
import threading
from datetime import datetime, timezone, timedelta

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 5930965838

app = Client("methstars", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

if os.path.exists("data.json"):
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
    client.send_chat_action(message.chat.id, ChatAction.TYPING)
    client.send_message(message.chat.id, f"{animation}
💊 *Welcome to MethStars* 💊
Choose your vice below:
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
    if cmd == "dice":
        client.send_message(cb.message.chat.id, "/dice 100")
    elif cmd == "slots":
        client.send_message(cb.message.chat.id, "/slots 100")
    elif cmd == "unbox":
        client.send_message(cb.message.chat.id, "/unbox")
    elif cmd == "lotto":
        client.send_message(cb.message.chat.id, "/lotto")
    elif cmd == "vault":
        client.send_message(cb.message.chat.id, "/vault")
    elif cmd == "top":
        client.send_message(cb.message.chat.id, "/top")
    elif cmd == "feed":
        client.send_message(cb.message.chat.id, "📈 Hype feed triggered!")
    elif cmd == "confetti":
        client.send_message(cb.message.chat.id, "🎉✨✨ Confetti everywhere!!")
    elif cmd == "shop":
        client.send_message(cb.message.chat.id, "/shop")

@app.on_message(filters.command("shop"))
def show_shop(client, message: Message):
    items = [
        {"label": "🧪 0.1g Blue Crystal - 200 ⭐", "price": 200, "item": "🧪 0.1g Blue Crystal"},
        {"label": "💊 0.1g Red Rock - 210 ⭐", "price": 210, "item": "💊 0.1g Red Rock"},
        {"label": "🧪 0.5g Flake - 470 ⭐", "price": 470, "item": "🧪 0.5g Flake"},
        {"label": "💊 0.5g Ice Pure - 500 ⭐", "price": 500, "item": "💊 0.5g Ice Pure"},
        {"label": "👑 1g Crystal Meth - 1000 ⭐", "price": 1000, "item": "👑 1g Crystal Meth"},
        {"label": "👑 1g Rainbow Shard - 1050 ⭐", "price": 1050, "item": "👑 1g Rainbow Shard"}
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
    prices = {
        "🧪 0.1g Blue Crystal": 200,
        "💊 0.1g Red Rock": 210,
        "🧪 0.5g Flake": 470,
        "💊 0.5g Ice Pure": 500,
        "👑 1g Crystal Meth": 1000,
        "👑 1g Rainbow Shard": 1050
    }

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
🎉 JACKPOT!!! {reward} ⭐ raining on you! 💰✨"
    else:
        u["stars"] -= amt
        result = f"{''.join(spin)}
💀 You lost {amt} ⭐ — Trap life hurts..."
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

@app.on_message(filters.command("dice"))
def dice_game(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].setdefault(uid, {"stars": 1000})
    try:
        amt = int(message.text.split()[1])
        if amt <= 0 or u["stars"] < amt:
            return message.reply("❌ Not enough Stars!")
        roll = random.choice([True, False])
        if roll:
            u["stars"] += amt
            res = f"🎲 WIN! You gained {amt} ⭐"
        else:
            u["stars"] -= amt
            res = f"💀 LOSS! You lost {amt} ⭐"
        save()
        message.reply(res)
    except:
        message.reply("Usage: /dice [amount]")

@app.on_message(filters.command("vault"))
def vault_view(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].get(uid, {"stars": 0, "inventory": [], "xp": 0})
    message.reply(f"📊 Vault:
⭐ Stars: {u['stars']}
🎒 Inventory Items: {len(u['inventory'])}
📈 XP: {u.get('xp', 0)}")

@app.on_message(filters.command("top"))
def top_players(client, message: Message):
    top = sorted(data["users"].items(), key=lambda x: x[1].get("stars", 0), reverse=True)[:5]
    board = "🏆 Top Meth Users:
"
    for i, (uid, u) in enumerate(top):
        board += f"{i+1}. User {uid[-4:]} — {u['stars']} ⭐
"
    message.reply(board)

@app.on_message(filters.command("lotto"))
def enter_lotto(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].setdefault(uid, {"stars": 1000})
    if u["stars"] < 100:
        return message.reply("🎟️ You need 100 ⭐ to enter the lottery!")
    if uid in data["lottery"]["entries"]:
        return message.reply("⏳ Already entered this round.")
    u["stars"] -= 100
    data["lottery"]["entries"].append(uid)
    save()
    message.reply("✅ You're in the next draw! Prize: 3000 ⭐")

@app.on_message(filters.command("inventory"))
def view_inventory(client, message: Message):
    uid = str(message.from_user.id)
    u = data["users"].get(uid, {"inventory": []})
    if not u["inventory"]:
        return message.reply("🎒 Inventory empty.")
    items = '
'.join(u["inventory"][-5:])
    message.reply(f"🎒 Recent Inventory:
{items}")

@app.on_message(filters.command("admin"))
def admin_dashboard(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        return message.reply("⛔ You do not have admin access.")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 User Count", callback_data="admin_users"), InlineKeyboardButton("💰 Total Stars", callback_data="admin_total")],
        [InlineKeyboardButton("🧹 Reset Lottery", callback_data="admin_reset_lottery")]
    ])
    message.reply("🛠️ Admin Panel:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_"))
def handle_admin_buttons(client, cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return cb.answer("Unauthorized", show_alert=True)
    cmd = cb.data.replace("admin_", "")
    if cmd == "users":
        cb.message.reply(f"👥 Total users: {len(data['users'])}")
    elif cmd == "total":
        total = sum(u.get("stars", 0) for u in data['users'].values())
        cb.message.reply(f"💰 Total Stars in circulation: {total}")
    elif cmd == "reset_lottery":
        data["lottery"] = {"entries": [], "last_draw": datetime.now(timezone.utc).isoformat()}
        save()
        cb.message.reply("🔁 Lottery has been reset.")

# Start enhanced loop
loop_fake_feed()
def run_lottery():
    now = datetime.now(timezone.utc)
    if data["lottery"]["entries"]:
        winner = random.choice(data["lottery"]["entries"])
        data["users"][winner]["stars"] += 3000
        for uid in data["users"]:
            try:
                app.send_message(int(uid), f"🎉 User {winner[-4:]} won the hourly Meth Lottery! +3000 ⭐")
            except: continue
    data["lottery"] = {"entries": [], "last_draw": now.isoformat()}
    save()
    threading.Timer(3600, run_lottery).start()

run_lottery()
