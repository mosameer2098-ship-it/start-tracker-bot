import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

REQUIRED_CHANNEL = "@KahaniyonKaGhar"
ADMIN_ID = 8132623749

app = Client(
    "bot_session_v5", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
)

AUTO_MSG = None


# Users save karne ka function
def save_user(user_id, referrer_id=None):
  if not os.path.exists("users.txt"):
    with open("users.txt", "w") as f:
      f.write("")

  with open("users.txt", "r") as f:
    users = f.read().splitlines()

  if str(user_id) not in users:
    with open("users.txt", "a") as f:
      f.write(str(user_id) + "\n")


# Groups save karne ka function (Jahan bot add hoga)
def save_group(chat_id):
  if not os.path.exists("groups.txt"):
    with open("groups.txt", "w") as f:
      f.write("")

  with open("groups.txt", "r") as f:
    groups = f.read().splitlines()

  if str(chat_id) not in groups:
    with open("groups.txt", "a") as f:
      f.write(str(chat_id) + "\n")


# Force Subscribe Check Function
async def check_subscription(client, user_id):
  if not REQUIRED_CHANNEL:
    return True
  try:
    member = await client.get_chat_member(REQUIRED_CHANNEL, user_id)
    if member.status in ["member", "administrator", "creator"]:
      return True
  except Exception:
    pass
  return False


# Background Auto Broadcast (Users + Groups dono ke liye)
async def auto_broadcast_loop():
  await asyncio.sleep(15)
  while True:
    await asyncio.sleep(600)  # 10 minutes
    global AUTO_MSG
    if AUTO_MSG:
      # Send to Users
      if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
          users = f.read().splitlines()
        for uid in users:
          try:
            user_id = int(uid)
            if AUTO_MSG.reply_to_message:
              await AUTO_MSG.reply_to_message.copy(user_id)
            else:
              await app.send_message(user_id, AUTO_MSG.text.split(None, 1)[1])
          except Exception:
            pass

      # Send to Groups
      if os.path.exists("groups.txt"):
        with open("groups.txt", "r") as f:
          groups = f.read().splitlines()
        for gid in groups:
          try:
            chat_id = int(gid)
            if AUTO_MSG.reply_to_message:
              await AUTO_MSG.reply_to_message.copy(chat_id)
            else:
              await app.send_message(chat_id, AUTO_MSG.text.split(None, 1)[1])
          except Exception:
            pass


# Har message par check karega ki bot kisi group mein add hua hai kya
@app.on_message(filters.group)
async def group_watcher(client, message):
  save_group(message.chat.id)


# Start Command (Private chat only)
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
  user = message.from_user
  user_id = user.id
  name = user.first_name
  username = f"@{user.username}" if user.username else "N/A"

  if REQUIRED_CHANNEL:
    is_joined = await check_subscription(client, user_id)
    if not is_joined:
      keyboard = InlineKeyboardMarkup([
          [
              InlineKeyboardButton(
                  "📢 Join Channel Now",
                  url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}",
              )
          ],
          [
              InlineKeyboardButton(
                  "🔄 Verify & Start",
                  url=f"https://t.me/{client.me.username}?start=start",
              )
          ],
      ])
      await message.reply_text(
          f"👋 Hello {name}!\n\n❌ **Pehle aapko hamara channel join karna hoga**"
          f" bot use karne ke liye:\n\n👉 {REQUIRED_CHANNEL}\n\nChannel join"
          " karne ke baad **'Verify & Start'** par click karein!",
          reply_markup=keyboard,
      )
      return

  save_user(user_id)

  group_msg = (
      f"🔔 **New User Started Bot!**\n\n"
      f"• **Name:** {name}\n"
      f"• **Username:** {username}\n"
      f"• **User ID:** `{user_id}`"
  )
  try:
    await client.send_message(GROUP_ID, group_msg)
  except Exception:
    pass

  await message.reply_text(
      f"✨ **Welcome, {name}!**\n🎬 Yahan aapko milti hain best stories aur free"
      " videos!"
  )


# Total users & groups check karne ke liye (/users)
@app.on_message(
    filters.command("users") & filters.private & filters.user(ADMIN_ID)
)
async def total_users_handler(client, message):
  user_count = 0
  group_count = 0

  if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
      user_count = len(f.read().splitlines())

  if os.path.exists("groups.txt"):
    with open("groups.txt", "r") as f:
      group_count = len(f.read().splitlines())

  await message.reply_text(
      f"📊 **Bot Statistics:**\n\n• **Total Private Users:**"
      f" `{user_count}`\n• **Total Connected Groups:** `{group_count}`"
  )


# Broadcast Command (Users + Groups dono ko jayega)
@app.on_message(
    filters.command(["broadcast", "brodcast"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def broadcast_handler(client, message):
  if not message.reply_to_message and len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya message likhein ya kisi message ko reply karein!**"
    )
    return

  sent_msg = await message.reply_text(
      "⏳ **Broadcast shuru ho gaya hai (Users & Groups)...**"
  )
  success = 0
  failed = 0

  # Send to Users
  if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
      users = f.read().splitlines()
    for uid in users:
      try:
        user_id = int(uid)
        if message.reply_to_message:
          await message.reply_to_message.copy(user_id)
        else:
          broadcast_content = message.text.split(None, 1)[1]
          await client.send_message(user_id, broadcast_content)
        success += 1
      except Exception:
        failed += 1

  # Send to Groups
  if os.path.exists("groups.txt"):
    with open("groups.txt", "r") as f:
      groups = f.read().splitlines()
    for gid in groups:
      try:
        chat_id = int(gid)
        if message.reply_to_message:
          await message.reply_to_message.copy(chat_id)
        else:
          broadcast_content = message.text.split(None, 1)[1]
          await client.send_message(chat_id, broadcast_content)
        success += 1
      except Exception:
        failed += 1

  await sent_msg.edit_text(
      f"✅ **Broadcast Poora Ho Gaya!**\n\n• **Successfully Sent:**"
      f" `{success}`\n• **Failed:** `{failed}`"
  )


# Auto Broadcast Set command
@app.on_message(
    filters.command(["setauto", "setbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def set_auto_msg(client, message):
  global AUTO_MSG
  if not message.reply_to_message and len(message.command) < 2:
    await message.reply_text("❌ **Kripya message likhein ya reply karein!**")
    return

  AUTO_MSG = message
  await message.reply_text(
      "✅ **10-Minutes Automatic Broadcast (Users + Groups) set ho gaya hai!**"
  )


# Stop Auto Broadcast
@app.on_message(
    filters.command(["stopauto", "stopbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def stop_auto_msg(client, message):
  global AUTO_MSG
  AUTO_MSG = None
  await message.reply_text("🛑 **Automatic Broadcast band kar diya gaya hai!**")


async def main():
  asyncio.create_task(auto_broadcast_loop())


print("Group Support Broadcast Bot start ho raha hai...")
app.start()
asyncio.get_event_loop().run_until_complete(main())

from pyrogram import idle

idle()
app.stop()

