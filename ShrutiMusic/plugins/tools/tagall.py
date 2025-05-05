import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait
import random
import re

from ShrutiMusic import app

SPAM_CHATS = []
EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️",
    "🦋🐇🐀🐈🐈‍⬛",
    "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇",
    "🍴🍽️🔪🍶🥃",
    "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐",
    "🦩🦀🦑🐙🦪",
    "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨",
    "🥬🍉🧁🧇",
]

def clean_text(text):
    """Escape markdown special characters"""
    if not text:
        return ""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    return user_id in admin_ids

@app.on_message(
    filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "@"])
)
async def tag_all_users(_, message):
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return await message.reply_text("Only admins can use this command.")

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "Tagging process is already running. Use /cancel to stop it."
        )
    
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "Give some text to tag all, like: `@all Hi Friends`"
        )
    
    total_members = 0
    tagged_members = 0
    
    try:
        # Get total members count
        async for _ in app.get_chat_members(message.chat.id):
            total_members += 1
        
        SPAM_CHATS.append(message.chat.id)
        
        if replied:
            usernum = 0
            usertxt = ""
            
            async for m in app.get_chat_members(message.chat.id):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                
                tagged_members += 1
                usernum += 1
                
                if usernum == 1:
                    emoji_sequence = random.choice(EMOJI)
                    emoji_index = 0
                
                emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
                usertxt += f"[{emoji}](tg://user?id={m.user.id}) "
                emoji_index += 1
                
                if usernum == 5:
                    await replied.reply_text(
                        usertxt,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(1)
                    usernum = 0
                    usertxt = ""
            
            if usernum != 0:
                await replied.reply_text(
                    usertxt,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            usernum = 0
            usertxt = ""
            text = clean_text(message.text.split(None, 1)[1])
            
            async for m in app.get_chat_members(message.chat.id):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                
                tagged_members += 1
                usernum += 1
                
                if usernum == 1:
                    emoji_sequence = random.choice(EMOJI)
                    emoji_index = 0
                
                emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
                usertxt += f"[{emoji}](tg://user?id={m.user.id}) "
                emoji_index += 1
                
                if usernum == 5:
                    await app.send_message(
                        message.chat.id,
                        f"{text}\n{usertxt}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(2)
                    usernum = 0
                    usertxt = ""
            
            if usernum != 0:
                await app.send_message(
                    message.chat.id,
                    f"{text}\n\n{usertxt}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        summary_msg = f"""
✅ Tagging completed!

Total members: {total_members}
Tagged members: {tagged_members}
"""
        await app.send_message(message.chat.id, summary_msg)
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        await app.send_message(message.chat.id, f"An error occurred: {str(e)}")
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass

@app.on_message(
    filters.command(["admintag", "adminmention", "admins", "report"], prefixes=["/", "@"])
)
async def tag_all_admins(_, message):
    if not message.from_user:
        return
    
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return await message.reply_text("Only admins can use this command.")

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "Tagging process is already running. Use /cancel to stop it."
        )
    
    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "Give some text to tag admins, like: `@admins Hi Friends`"
        )
    
    total_admins = 0
    tagged_admins = 0
    
    try:
        async for _ in app.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            total_admins += 1
        
        SPAM_CHATS.append(message.chat.id)
        
        if replied:
            adminnum = 0
            admintxt = ""
            
            async for m in app.get_chat_members(
                message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                
                tagged_admins += 1
                adminnum += 1
                
                if adminnum == 1:
                    emoji_sequence = random.choice(EMOJI)
                    emoji_index = 0
                
                emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
                admintxt += f"[{emoji}](tg://user?id={m.user.id}) "
                emoji_index += 1
                
                if adminnum == 5:
                    await replied.reply_text(
                        admintxt,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(1)
                    adminnum = 0
                    admintxt = ""
            
            if adminnum != 0:
                await replied.reply_text(
                    admintxt,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            adminnum = 0
            admintxt = ""
            text = clean_text(message.text.split(None, 1)[1])
            
            async for m in app.get_chat_members(
                message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                
                tagged_admins += 1
                adminnum += 1
                
                if adminnum == 1:
                    emoji_sequence = random.choice(EMOJI)
                    emoji_index = 0
                
                emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
                admintxt += f"[{emoji}](tg://user?id={m.user.id}) "
                emoji_index += 1
                
                if adminnum == 5:
                    await app.send_message(
                        message.chat.id,
                        f"{text}\n{admintxt}",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(2)
                    adminnum = 0
                    admintxt = ""
            
            if adminnum != 0:
                await app.send_message(
                    message.chat.id,
                    f"{text}\n\n{admintxt}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        summary_msg = f"""
✅ Admin tagging completed!

Total admins: {total_admins}
Tagged admins: {tagged_admins}
"""
        await app.send_message(message.chat.id, summary_msg)
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        await app.send_message(message.chat.id, f"An error occurred: {str(e)}")
    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass

@app.on_message(
    filters.command(
        [
            "stopmention",
            "cancel",
            "cancelmention",
            "offmention",
            "mentionoff",
            "cancelall",
        ],
        prefixes=["/", "@"],
    )
)
async def cancelcmd(_, message):
    chat_id = message.chat.id
    admin = await is_admin(chat_id, message.from_user.id)
    if not admin:
        return await message.reply_text("Only admins can use this command.")

    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        return await message.reply_text("Tagging process successfully stopped!")
    else:
        return await message.reply_text("No tagging process is currently running!")

MODULE = "Tᴀɢᴀʟʟ"
HELP = """
@all or /all | /tagall or @tagall | /mentionall or @mentionall [text] or [reply to any message] - Tag all users in your group with random emojis (changes every 5 users)

/admintag or @admintag | /adminmention or @adminmention | /admins or @admins [text] or [reply to any message] - Tag all admins in your group with random emojis (changes every 5 users)

/stopmention or @stopmention | /cancel or @cancel | /offmention or @offmention | /mentionoff or @mentionoff | /cancelall or @cancelall - Stop any running tagging process

Note: 
1. These commands can only be used by admins
2. The bot and assistant must be admins in your group
3. Users will be tagged with random emojis that link to their profiles
4. After completion, you'll get a summary with counts
5. Tags 5 users at a time with unique emoji sequence for each batch
"""
