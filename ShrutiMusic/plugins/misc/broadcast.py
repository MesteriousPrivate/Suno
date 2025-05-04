import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, MessageEntityType
from pyrogram.errors import FloodWait
from pyrogram.types import MessageEntity

from ShrutiMusic import app
from ShrutiMusic.misc import SUDOERS
from ShrutiMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from ShrutiMusic.utils.decorators.language import language
from ShrutiMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False

async def copy_message_with_entities(client, chat_id, original_message):
    """Copy message with all formatting and buttons (no forward tag)"""
    text = original_message.text or original_message.caption or ""
    entities = original_message.entities or original_message.caption_entities
    
    kwargs = {
        "chat_id": chat_id,
        "reply_markup": original_message.reply_markup,
        "disable_web_page_preview": True,  # Disable link preview
    }
    
    if entities:
        kwargs["entities" if original_message.text else "caption_entities"] = entities
    
    if original_message.photo:
        return await client.send_photo(
            photo=original_message.photo.file_id,
            caption=text,
            **kwargs
        )
    elif original_message.video:
        return await client.send_video(
            video=original_message.video.file_id,
            caption=text,
            **kwargs
        )
    elif original_message.audio:
        return await client.send_audio(
            audio=original_message.audio.file_id,
            caption=text,
            **kwargs
        )
    elif original_message.document:
        return await client.send_document(
            document=original_message.document.file_id,
            caption=text,
            **kwargs
        )
    else:
        return await client.send_message(
            text=text,
            **kwargs
        )

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    
    # Handle -wfchat and -wfuser flags (from original Shruti script)
    if "-wfchat" in message.text or "-wfuser" in message.text:
        if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.text):
            return await message.reply_text("Please reply to a text or image message for broadcasting.")

        if message.reply_to_message.photo:
            content_type = 'photo'
            file_id = message.reply_to_message.photo.file_id
        else:
            content_type = 'text'
            text_content = message.reply_to_message.text
            
        caption = message.reply_to_message.caption
        reply_markup = message.reply_to_message.reply_markup if hasattr(message.reply_to_message, 'reply_markup') else None

        IS_BROADCASTING = True
        await message.reply_text(_["broad_1"])

        if "-wfchat" in message.text:
            sent_chats = 0
            chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
            for i in chats:
                try:
                    if content_type == 'photo':
                        await app.send_photo(chat_id=i, photo=file_id, caption=caption, reply_markup=reply_markup)
                    else:
                        await app.send_message(chat_id=i, text=text_content, reply_markup=reply_markup)
                    sent_chats += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(fw.x)
                except:
                    continue
            await message.reply_text(f"Broadcast to chats completed! Sent to {sent_chats} chats.")

        if "-wfuser" in message.text:
            sent_users = 0
            users = [int(user["user_id"]) for user in await get_served_users()]
            for i in users:
                try:
                    if content_type == 'photo':
                        await app.send_photo(chat_id=i, photo=file_id, caption=caption, reply_markup=reply_markup)
                    else:
                        await app.send_message(chat_id=i, text=text_content, reply_markup=reply_markup)
                    sent_users += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(fw.x)
                except:
                    continue
            await message.reply_text(f"Broadcast to users completed! Sent to {sent_users} users.")

        IS_BROADCASTING = False
        return

    # Main broadcast handler (from Champu script)
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        # Remove all flags
        for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user", "-noforward"]:
            query = query.replace(flag, "")
        if not query.strip():
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # Broadcast to groups
    if "-nobot" not in message.text:
        sent = pin = 0
        chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
        for chat_id in chats:
            try:
                if message.reply_to_message:
                    if "-noforward" in message.text:
                        m = await copy_message_with_entities(app, chat_id, message.reply_to_message)
                    else:
                        m = await app.forward_messages(chat_id, y, x)
                else:
                    m = await app.send_message(
                        chat_id, 
                        text=query,
                        disable_web_page_preview=True
                    )
                
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except: continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except: continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except: continue
        
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except: pass

    # Broadcast to users
    if "-user" in message.text:
        susr = 0
        users = [int(user["user_id"]) for user in await get_served_users()]
        for user_id in users:
            try:
                if message.reply_to_message:
                    if "-noforward" in message.text:
                        m = await copy_message_with_entities(app, user_id, message.reply_to_message)
                    else:
                        m = await app.forward_messages(user_id, y, x)
                else:
                    m = await app.send_message(
                        user_id,
                        text=query,
                        disable_web_page_preview=True
                    )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except: pass
        
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except: pass

    # Broadcast via assistants
    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from ShrutiMusic.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    if message.reply_to_message:
                        if "-noforward" in message.text:
                            m = await copy_message_with_entities(client, dialog.chat.id, message.reply_to_message)
                        else:
                            m = await client.forward_messages(dialog.chat.id, y, x)
                    else:
                        m = await client.send_message(
                            dialog.chat.id,
                            text=query,
                            disable_web_page_preview=True
                        )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    await asyncio.sleep(fw.value)
                except: continue
            text += _["broad_7"].format(num, sent)
        
        try:
            await aw.edit_text(text)
        except: pass

    IS_BROADCASTING = False

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except: continue

asyncio.create_task(auto_clean())
