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


# Function: User ID ko text file mein save karne ke liye
def save_user(user_id):
  if not os.path.exists("users.txt"):
    with open("users.txt", "w") as f:
      f.write("")

  with open("users.txt", "r") as f:
    users = f.read().splitlines()

  if str(user_id) not in users:
    with open("users.txt", "a") as f:
      f.write(str(user_id) + "\n")


# 1. /start command handler
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
  user = message.from_user
  name = user.first_name
  username = f"@{user.username}" if user.username else "N/A"
  user_id = user.id

  # User ID ko file mein save karein
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


# 2. /broadcast command handler (Sirf Admin ke liye)
@app.on_message(
    filters.command("broadcast") & filters.private & filters.user(ADMIN_ID)
)
async def broadcast_handler(client, message):
  if not message.reply_to_message and len(message.command) < 2:
    await message.reply_text(
        "❌ **Kripya broadcast karne ke liye message likhein ya kisi message ko"
        " reply karein!**\n\nExample: `/broadcast Hello dosto!`"
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


app.start()
print("Bot successfully start ho gaya hai aur file-based broadcast active hai!")
idle()
