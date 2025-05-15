from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPermissions
from pymongo import MongoClient
from ShrutiMusic import app
import asyncio
from ShrutiMusic.misc import SUDOERS
from config import MONGO_DB_URI
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import (
    ChatAdminRequired,
    UserNotParticipant,
)

fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if not (member.status == "creator" or user_id in SUDOERS):
        return await message.reply_text("<b>Only group owners or sudoers can use this command.</b>", parse_mode=ParseMode.HTML)

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text("<b>Force subscription has been disabled for this group.</b>", parse_mode=ParseMode.HTML)

    if len(message.command) != 2:
        return await message.reply_text("<b>Usage: /fsub <channel username or id> or /fsub off to disable</b>", parse_mode=ParseMode.HTML)

    channel_input = message.command[1]

    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_username = f"{channel_info.username}" if channel_info.username else None

        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True
        )

        await message.reply_text(
            f"<b>🎉 Force subscription set to channel:</b> <a href='https://t.me/{channel_username}'>{channel_info.title}</a>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.reply_text("<b>🚫 Failed to set force subscription.</b>", parse_mode=ParseMode.HTML)
        
@app.on_chat_member_updated()
async def on_user_join(client: Client, chat_member_updated):
    chat_id = chat_member_updated.chat.id
    user_id = chat_member_updated.from_user.id
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})

    if not forcesub_data:
        return  # No force subscription set for this group

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    new_chat_member = chat_member_updated.new_chat_member
    if new_chat_member is None:
        return  # Exit if new_chat_member is None

    # Check if the user joined the group
    if new_chat_member.status == "member":
        try:
            # Check if the user is a member of the channel
            user_member = await app.get_chat_member(channel_id, user_id)
            # If the user is a member of the channel, do nothing
            return
        except UserNotParticipant:
            # User is not a member of the channel, mute them
            await client.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await client.send_message(
                chat_id,
                f"<b>🚫 {chat_member_updated.from_user.mention}, you have been muted because you need to join the <a href='https://t.me/{channel_username}'>channel</a> to send messages in this group.</b>",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            # Handle any other exceptions if necessary
            print(f"Error checking channel membership: {e}")
    else:
        # If the user is no longer a member, check if they can be unmuted
        try:
            user_member = await app.get_chat_member(channel_id, user_id)
            # If the user is now a member of the channel, unmute them
            if user_member.status == "member":
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=True)
                await client.send_message(
                    chat_id,
                    f"<b>🎉 {chat_member_updated.from_user.mention}, you have been unmuted because you joined the <a href='https://t.me/{channel_username}'>channel</a>.</b>",
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
        except UserNotParticipant:
            # User is still not a member of the channel, do nothing
            pass
        except Exception as e:
            # Handle any other exceptions if necessary
            print(f"Error checking channel membership on unmute: {e}")
            
@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("Closed!")
    await callback_query.message.delete()
    

async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the message has a from_user attribute
    if message.from_user is None:
        return  # Exit if the message does not come from a user

    user_id = message.from_user.id
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    try:
        user_member = await app.get_chat_member(channel_id, user_id)
        if user_member:
            return
    except UserNotParticipant:
        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
        else:
            invite_link = await app.export_chat_invite_link(channel_id)
            channel_url = invite_link
        await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=f"<b>👋 Hello {message.from_user.mention},</b>\n\n<b>You need to join the <a href='{channel_url}'>channel</a> to send messages in this group.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("๏ Join Channel ๏", url=channel_url)]]),
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(1)
    except ChatAdminRequired:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text("<b>🚫 I'm no longer an admin in the forced subscription channel. Force subscription has been disabled.</b>", parse_mode=ParseMode.HTML)

@app.on_message(filters.group, group=30)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        return


__MODULE__ = "Fsub"
__HELP__ = """
<b>/fsub</b> <channel username or id> - Set force subscription for this group.
<b>/fsub off</b> - Disable force subscription for this group.
"""
