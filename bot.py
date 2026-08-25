import asyncio
import os
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

ADMIN_ID = 8132623749

app = Client(
    "start_tracker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
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


# Background Auto Broadcast Task (Har 60 seconds / 1 minute mein)
async def auto_broadcast_loop():
  await asyncio.sleep(15)  # Bot start hone ka 15 second wait karega
  while True:
    await asyncio.sleep(60)  # 1 minute wait
    global AUTO_MSG
    if AUTO_MSG and os.path.exists("users.txt"):
      with open("users.txt", "r") as f:
        users = f.read().splitlines()

      for uid in users:
        try:
          user_id = int(uid)
          await app.send_message(user_id, AUTO_MSG)
        except Exception:
          pass  # Blocked users ko ignore karega


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


# Total users check karne ke liye
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

  broadcast_content = message.reply_to_message or message.text.split(None, 1)[1]

  with open("users.txt", "r") as f:
    users = f.read().splitlines()

  for uid in users:
    try:
      user_id = int(uid)
      if message.reply_to_message:
        await message.reply_to_message.copy(user_id)
      else:
        await client.send_message(user_id, broadcast_content)
      success += 1
    except Exception:
      failed += 1

  await sent_msg.edit_text(
      f"✅ **Broadcast Poora Ho Gaya!**\n\n"
      f"• **Successfully Sent:** `{success}`\n"
      f"• **Failed (Blocked bot):** `{failed}`"
  )


# Auto Broadcast Message Set karne ki command
@app.on_message(
    filters.command(["setauto", "setbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def set_auto_msg(client, message):
  global AUTO_MSG
  if len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya message likhein!**\nExample: `/setauto Yeh message har 1"
        " minute baad jayega.`"
    )
    return

  AUTO_MSG = message.text.split(None, 1)[1]
  await message.reply_text(
      "✅ **1-Minute Automatic Broadcast set ho gaya hai!**\nAb ye message har 1"
      f" minute mein sabhi users ko jayega:\n\n`{AUTO_MSG}`"
  )


# Main function jo background task aur bot ko ek sath run karega
async def main():
  # Background task ko loop mein dal rahe hain
  asyncio.create_task(auto_broadcast_loop())
  await app.start()
  print("Bot successfully start ho gaya hai aur 1-min auto broadcast active hai!")
  from pyrogram import idle

  await idle()
  await app.stop()


# Heroku par error-free run karne ke liye
if __name__ == "__main__":
  asyncio.run(main())
