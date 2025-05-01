from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters
import random
import config
from ShrutiMusic import app

# Start panel buttons
def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons

# Private panel with View My Source in desired position
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="View My Source", callback_data="view_source")
        ],
        [
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_GROUP),
        ],
        [
            InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")
        ],
    ]
    return buttons

# Video list
SOURCE_VIDEOS = [
    "https://files.catbox.moe/xjihw1.mp4",
    "https://files.catbox.moe/z3f1wi.mp4",
]

# Handle "View My Source"
@app.on_callback_query(filters.regex("view_source"))
async def view_source_callback(client, callback_query):
    video_url = random.choice(SOURCE_VIDEOS)
    try:
        await callback_query.message.edit_media(
            media=video_url,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Source Now", callback_data="view_now_popup")],
                [InlineKeyboardButton("Back", callback_data="back_to_panel")]
            ])
        )
    except Exception as e:
        await callback_query.answer("Video send failed!", show_alert=True)

# Alert for "View Source Now"
@app.on_callback_query(filters.regex("view_now_popup"))
async def view_now_popup(client, callback_query):
    await callback_query.answer("OWNER SE BAT KARO", show_alert=True)

# Back button to restore private panel
@app.on_callback_query(filters.regex("back_to_panel"))
async def back_to_panel(client, callback_query):
    from ShrutiMusic.utils.inline import private_panel  # Ensure correct import
    lang = await app.get_lang(callback_query.message.chat.id)
    await callback_query.message.edit_text(
        text=lang["START_TEXT"],  # Use your actual start message
        reply_markup=InlineKeyboardMarkup(private_panel(lang)),
        disable_web_page_preview=True
    )
