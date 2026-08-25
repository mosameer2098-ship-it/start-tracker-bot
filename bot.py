import os
from pyrogram import Client, filters, idle

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

app = Client(
    "start_tracker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
)


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
  user = message.from_user
  name = user.first_name
  username = f"@{user.username}" if user.username else "N/A"
  user_id = user.id

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


# Seedha start karke idle chod do, koi crash nahi hoga
app.start()
print("Bot successfully start ho gaya hai aur ab live hai!")
idle()
