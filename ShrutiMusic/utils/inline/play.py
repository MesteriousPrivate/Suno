import math
import random
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ShrutiMusic.utils.formatters import time_to_seconds

# Love Sentence Bar
def get_love_sentence_bar(played_sec: int, total_sec: int) -> str:
    love_lines = [
        "❤️ Lᴏᴠᴇ ɪɴ ᴇᴠᴇʀʏ ʙᴇᴀᴛ...",
        "❣️ Fᴇᴇʟ ᴛʜᴇ ᴍᴜsɪᴄ, Fᴇᴇʟ ᴍᴇ...",
        "💓 Tᴜɴᴇ ɪɴᴛᴏ ᴏᴜʀ ʜᴇᴀʀᴛs...",
        "💖 Wʜᴇɴ ʏᴏᴜ ᴘʟᴀʏ, ɪ ᴍᴇʟᴛ...",
        "💕 Eᴠᴇʀʏ ʙᴇᴀᴛ ɪs ғᴏʀ ʏᴏᴜ...",
        "💘 Lᴇᴛ ᴍᴇ sɪɴɢ ʏᴏᴜʀ ɴᴀᴍᴇ...",
        "💝 Mʏ sᴏᴜʟ ᴅᴀɴᴄᴇs ᴡɪᴛʜ ʏᴏᴜ...",
        "♥️ Yᴏᴜ + Mᴜsɪᴄ = Mᴀɢɪᴄ...",
        "❥ I ʟᴏᴠᴇ ʏᴏᴜ ʟɪᴋᴇ ʟʏʀɪᴄs ʟᴏᴠᴇ ʙᴇᴀᴛs...",
        "💞 Oɴ ʀᴇᴘᴇᴀᴛ: Yᴏᴜ.",
    ]
    index = (played_sec // 5) % len(love_lines)
    return love_lines[index]

# Progress Bar Function
def get_progress_bar(played: int, total: int) -> str:
    percent = (played / total) * 100
    full = int(percent // 10)
    empty = 10 - full
    bar = "▶️ " + "█" * full + "─" * empty + f" {int(percent)}%"
    return bar

# Inline Keyboard Generator
def generate_inline_keyboard(played_sec: int, total_sec: int) -> InlineKeyboardMarkup:
    love_text = get_love_sentence_bar(played_sec, total_sec)
    bar = get_progress_bar(played_sec, total_sec)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=love_text, url="https://t.me/ShrutiBots")],
        [InlineKeyboardButton(text=bar, callback_data="progress_dummy")]
    ])
    return keyboard

# Wave Effect Progress Bar
def get_wave_effect_bar(played_sec, total_sec):
    try:
        percentage = (played_sec / total_sec) * 100
    except ZeroDivisionError:
        percentage = 0
    progress_index = int((percentage / 100) * 10)

    bars = ["◉", "●", "○", "◆", "◇", "▣", "▤", "▧", "▩", "⬤"]
    trail = ["—", "–", "─", "⎯", "⎼", "⎻"]

    wave_symbol = random.choice(bars)
    line = random.choice(trail)

    bar = ""
    for i in range(11):
        if i == progress_index:
            bar += wave_symbol
        else:
            bar += line

    return bar

# Track Markup for Buttons
def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons

# Stream Markup Timer
def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    progress_bar = get_wave_effect_bar(played_sec, duration_sec)

    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"{played} {progress_bar} {dur}",
                url="https://t.me/SunoXMusic_bot?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(text="Cʜᴀᴛ ʙᴏᴛ 💐", url="https://t.me/ShrutixRobot"),
            InlineKeyboardButton(text="Mᴀɴᴀɢᴇᴍᴇɴᴛ 🪷", url="https://t.me/ShrutixMusicBot"),
        ],
    ]
    return buttons

# Playlist Markup for Buttons
def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"AviaxPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"AviaxPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons

# Livestream Markup for Buttons
def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons

# Slider Markup for Buttons
def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
