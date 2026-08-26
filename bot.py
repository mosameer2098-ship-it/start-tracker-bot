import asyncio
import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

ADMIN_ID = 8132623749

app = Client(
    "bot_session_v3", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
)

AUTO_MSG = None


def save_user(user_id):
  if not os.path.exists("users.txt"):
    with open("users.txt", "w") as f:
      f.write("")

  with open("users.txt", "r") as f:
    users = f.read().splitlines()

  if str(user_id) not in users:
    with open("users.txt", "a") as f:
      f.write(str(user_id) + "\n")


# Background Auto Broadcast Task (Har 10 minutes mein)
async def auto_broadcast_loop():
  await asyncio.sleep(15)
  while True:
    await asyncio.sleep(600)  # 600 seconds = 10 minutes wait
    global AUTO_MSG
    if AUTO_MSG and os.path.exists("users.txt"):
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


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
  user = message.from_user
  name = user.first_name
  username = f"@{user.username}" if user.username else "N/A"
  user_id = user.id

  save_user(user_id)

  group_msg = (
      f"🔔 **New User Started Bot!**\n\n"
      f"• **Name:** {name}\n"
      f"• **Username:** {username}\n"
      f"• **User ID:** `{user_id}`"
  )

  try:
    await client.send_message(GROUP_ID, group_msg)
  except Exception as e:
    print(f"Group mein message bhejne mein error aaya: {e}")

  await message.reply_text(
      f"Hello {name}! Bot ko start karne ke liye dhanyawad."
  )


# Total users check karne ke liye command (/users)
@app.on_message(
    filters.command("users") & filters.private & filters.user(ADMIN_ID)
)
async def total_users_handler(client, message):
  if not os.path.exists("users.txt"):
    await message.reply_text("📊 **Total Active Users:** `0`")
    return

  with open("users.txt", "r") as f:
    users = f.read().splitlines()

  total_count = len(users)
  await message.reply_text(
      f"📊 **Bot Statistics:**\n\n• **Total Active Users:** `{total_count}`"
  )


# Instant Broadcast command
@app.on_message(
    filters.command(["broadcast", "brodcast"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def broadcast_handler(client, message):
  if not message.reply_to_message and len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya message likhein ya kisi message ko reply karein!**\n\nExample:"
        " `/broadcast Hello dosto!`"
    )
    return

  if not os.path.exists("users.txt"):
    await message.reply_text("❌ Abhi tak koi bhi user nahi hai database mein!")
    return

  sent_msg = await message.reply_text("⏳ **Broadcast shuru ho gaya hai...**")
  success = 0
  failed = 0

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

  await sent_msg.edit_text(
      f"✅ **Broadcast Poora Ho Gaya!**\n\n"
      f"• **Successfully Sent:** `{success}`\n"
      f"• **Failed (Blocked bot):** `{failed}`"
  )


# Auto Broadcast Set karne ki command
@app.on_message(
    filters.command(["setauto", "setbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def set_auto_msg(client, message):
  global AUTO_MSG
  if not message.reply_to_message and len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya message likhein ya kisi message ko reply karein!**\n\nExample:"
        " `/setauto Yeh message har 10 minute baad jayega.`"
    )
    return

  AUTO_MSG = message
  await message.reply_text(
      "✅ **10-Minutes Automatic Broadcast set ho gaya hai!**\nAb ye message har"
      " 10 minute mein sabhi users ko jata rahega."
  )


# Auto Broadcast off karne ki command (Nayi command)
@app.on_message(
    filters.command(["stopauto", "stopbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def stop_auto_msg(client, message):
  global AUTO_MSG
  AUTO_MSG = None
  await message.reply_text(
      "🛑 **Automatic Broadcast band kar diya gaya hai!**\nAb koi bhi auto"
      " message nahi jayega."
  )


async def main():
  asyncio.create_task(auto_broadcast_loop())


print("Bot successfully start ho raha hai...")
app.start()
asyncio.get_event_loop().run_until_complete(main())

from pyrogram import idle

idle()
app.stop()
