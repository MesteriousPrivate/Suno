from ShrutiMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineQueryResultArticle, 
    InputTextMessageContent,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from pyrogram.errors import UserIsBlocked

BOT_USERNAME = app.username

whisper_db = {}

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("💒 sᴛᴀʀᴛ ᴡʜɪsᴘᴇʀ", switch_inline_query_current_chat="")]])

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="💒 ᴡʜɪsᴘᴇʀ",
                description=f"@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(
                    f"💒 Usage:\n\n@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]"
                ),
                thumb_url="https://files.catbox.moe/i4h1y3.jpg",
                reply_markup=switch_btn
            )
        ]
    else:
        try:
            user_id = data.split()[0]
            msg = data.split(None, 1)[1]
        except IndexError:
            mm = [
                InlineQueryResultArticle(
                    title="💒 ᴡʜɪsᴘᴇʀ",
                    description="Invalid format!",
                    input_message_content=InputTextMessageContent(
                        "Invalid format! Use: @username message"
                    ),
                    thumb_url="https://files.catbox.moe/i4h1y3.jpg",
                    reply_markup=switch_btn
                )
            ]
            results.append(mm)
            return results
        
        try:
            user = await _.get_users(user_id)
        except Exception:
            mm = [
                InlineQueryResultArticle(
                    title="💒 ᴡʜɪsᴘᴇʀ",
                    description="ɪɴᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ!",
                    input_message_content=InputTextMessageContent(
                        "ɪɴᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ!"
                    ),
                    thumb_url="https://files.catbox.moe/i4h1y3.jpg",
                    reply_markup=switch_btn
                )
            ]
            results.append(mm)
            return results
        
        whisper_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "💒 ᴡʜɪsᴘᴇʀ", 
                callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}"
            )
        ]])
        
        one_time_whisper_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ", 
                callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one"
            )
        ]])
        
        mm = [
            InlineQueryResultArticle(
                title="💒 ᴡʜɪsᴘᴇʀ",
                description=f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}",
                input_message_content=InputTextMessageContent(
                    f"💒 ʏᴏᴜ ᴀʀᴇ sᴇɴᴅɪɴɢ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" 
                    if user.username else 
                    f"sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}.\n\nᴛʏᴘᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ/sᴇɴᴛᴇɴᴄᴇ."
                ),
                thumb_url="https://files.catbox.moe/i4h1y3.jpg",
                reply_markup=whisper_btn
            ),
            InlineQueryResultArticle(
                title="🔩 ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ",
                description=f"sᴇɴᴅ ᴀ ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" if user.username else f"sᴇɴᴅ ᴀ ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}",
                input_message_content=InputTextMessageContent(
                    f"🔩 ʏᴏᴜ ᴀʀᴇ sᴇɴᴅɪɴɢ ᴀ ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ᴛᴏ @{user.username}" 
                    if user.username else 
                    f"sᴇɴᴅ ᴀ ᴏɴᴇ-ᴛɪᴍᴇ ᴡʜɪsᴘᴇʀ ᴛᴏ {user.first_name}.\n\nᴛʏᴘᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ/sᴇɴᴛᴇɴᴄᴇ."
                ),
                thumb_url="https://files.catbox.moe/i4h1y3.jpg",
                reply_markup=one_time_whisper_btn
            )
        ]
        
        whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
    
    results.append(mm)
    return results

@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 1786683163]:
        try:
            await _.send_message(
                from_user, 
                f"{query.from_user.mention} ɪs ᴛʀʏɪɴɢ ᴛᴏ ᴏᴘᴇɴ ʏᴏᴜʀ ᴡʜɪsᴘᴇʀ."
            )
        except UserIsBlocked:
            pass
        except Exception as e:
            print(f"Error sending notification: {e}")
        
        return await query.answer("ᴛʜɪs ᴡʜɪsᴘᴇʀ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ 🚧", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    msg = whisper_db.get(search_msg, "🚫 ᴇʀʀᴏʀ!\n\nᴡʜɪsᴘᴇʀ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!")
    
    SWITCH = InlineKeyboardMarkup([[
        InlineKeyboardButton("ɢᴏ ɪɴʟɪɴᴇ 🪝", switch_inline_query_current_chat="")
    ]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text(
                "📬 ᴡʜɪsᴘᴇʀ ʜᴀs ʙᴇᴇɴ ʀᴇᴀᴅ!\n\nᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇɴᴅ ᴀ ᴡʜɪsᴘᴇʀ!",
                reply_markup=SWITCH
            )
            del whisper_db[search_msg]

async def in_help():
    answers = [
        InlineQueryResultArticle(
            title="💒 ᴡʜɪsᴘᴇʀ",
            description=f"@{BOT_USERNAME} [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(
                f"**📍ᴜsᴀɢᴇ:**\n\n@{BOT_USERNAME} (ᴛᴀʀɢᴇᴛ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ) (ʏᴏᴜʀ ᴍᴇssᴀɢᴇ).\n\n"
                f"**ᴇxᴀᴍᴘʟᴇ:**\n@{BOT_USERNAME} @username I Love You"
            ),
            thumb_url="https://files.catbox.moe/2oj1vp.webp",
            reply_markup=switch_btn
        )
    ]
    return answers

@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)
