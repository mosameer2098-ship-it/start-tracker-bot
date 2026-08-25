import asyncio
import os
from pyrogram import Client, filters, idle

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


@app.on_message(
    filters.command(["setauto", "setbrod"])
    & filters.private
    & filters.user(ADMIN_ID)
)
async def set_auto_msg(client, message):
  global AUTO_MSG
  if len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya message likhein!**\nExample: `/setauto Yeh message har 2"
        " minute baad jayega.`"
    )
    return

  AUTO_MSG = message.text.split(None, 1)[1]
  await message.reply_text(
      "✅ **Automatic Broadcast set ho gaya hai!**\nAb ye message har 2 minute"
      f" mein sabhi users ko jayega:\n\n`{AUTO_MSG}`"
  )


# Background loop jo ab properly background mein chalega
async def auto_broadcast_loop():
  while True:
    await asyncio.sleep(120)  # 2 minute ka wait
    global AUTO_MSG
    if AUTO_MSG and os.path.exists("users.txt"):
      with open("users.txt", "r") as f:
        users = f.read().splitlines()

      for uid in users:
        try:
          user_id = int(uid)
          await app.send_message(user_id, AUTO_MSG)
        except Exception:
          pass


async def main():
  await app.start()
  print("Bot successfully start ho gaya hai!")
  # Background task ko shuru kar rahe hain
  asyncio.create_task(auto_broadcast_loop())
  await idle()
  await app.stop()


asyncio.run(main())
