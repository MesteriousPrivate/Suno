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

# Private panel buttons with correct order
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

# List of source video URLs
SOURCE_VIDEOS = [
    "https://files.catbox.moe/xjihw1.mp4",
    "https://files.catbox.moe/z3f1wi.mp4",
]

# Callback handler for "View My Source"
@app.on_callback_query(filters.regex("view_source"))
async def view_source_callback(client, callback_query):
    video_url = random.choice(SOURCE_VIDEOS)
    await callback_query.message.reply_video(
        video=video_url,
        caption="<b>Here is your source file.</b>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("View Now", callback_data="view_now_popup")]]
        )
    )
    await callback_query.answer()

# Callback handler for "View Now" button
@app.on_callback_query(filters.regex("view_now_popup"))
async def view_now_popup(client, callback_query):
    await callback_query.answer(
        "OWNER SE BAT KARO", show_alert=True
    )
