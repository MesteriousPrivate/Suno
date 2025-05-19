# ===================================================
#                 🔱 𝙎𝙃𝙍𝙐𝙏𝙄  𝘽𝙊𝙏𝙎 🔱
#            ⚙️ CONFIGURATION FILE ⚙️
# ===================================================

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()  # 🌐 Loading Environment Variables

# ===================================================
# 🔐 BASIC AUTH & API CREDENTIALS
# ===================================================

API_ID = int(getenv("API_ID"))                        # 🆔 API ID from my.telegram.org
API_HASH = getenv("API_HASH")                         # 🔑 API HASH from my.telegram.org
BOT_TOKEN = getenv("BOT_TOKEN")                       # 🤖 Bot Token from @BotFather
OWNER_ID = int(getenv("OWNER_ID", 0))                 # 👑 Bot Owner Telegram ID
OWNER_USERNAME = getenv("OWNER_USERNAME", "WTF_WhyMeeh")  # 🙋 Owner Username

# ===================================================
# 🗃️ DATABASE & LOGGING
# ===================================================

MONGO_DB_URI = getenv("MONGO_DB_URI", None)           # 📦 MongoDB URI
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", 0))         # 📥 Group ID where logs are sent

# ===================================================
# ⚙️ DEPLOYMENT & GIT SETTINGS
# ===================================================

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")           # 🚀 Heroku App Name
HEROKU_API_KEY = getenv("HEROKU_API_KEY")             # 🔐 Heroku API Key

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/MesteriousPrivate/ShrutiMusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)                 # 🔒 GitHub Token for private repos

# ===================================================
# 🌍 API CONNECTIONS
# ===================================================

API_URL = getenv("API_URL", "https://api.thequickearn.xyz")  # ⚡ Song API URL
API_KEY = getenv("API_KEY", None)                            # 🔑 API Key from @WTF_WhyMeeh

# ===================================================
# 📡 MUSIC & STREAMING SETTINGS
# ===================================================

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))  # ⏱️ Duration Limit (in mins)

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))  # 📜 Max songs per playlist

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))     # 🎧 100MB
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2145386496))    # 🎥 ~2GB

# ===================================================
# 🎧 PYROGRAM SESSIONS (For Assistants)
# ===================================================

STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

# ===================================================
# 🧠 SPOTIFY INTEGRATION (Optional)
# ===================================================

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

# ===================================================
# 🧰 FEATURES & FLAGS
# ===================================================

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))
PRIVACY_LINK = getenv("PRIVACY_LINK", "https://graph.org/Privacy-Policy-05-01-30")

# ===================================================
# 🔗 SUPPORT & COMMUNITY LINKS
# ===================================================

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL")
SUPPORT_GROUP = getenv("SUPPORT_GROUP")

if SUPPORT_CHANNEL and not re.match("(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - SUPPORT_CHANNEL must start with https://")

if SUPPORT_GROUP and not re.match("(?:http|https)://", SUPPORT_GROUP):
    raise SystemExit("[ERROR] - SUPPORT_GROUP must start with https://")

# ===================================================
# 🖼️ IMAGE URLs FOR UI
# ===================================================

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/mwjsr7.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/j3k6jl.jpg"
STATS_IMG_URL = "https://files.catbox.moe/poxwf1.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
TELEGRAM_VIDEO_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"

# ===================================================
# 🔒 INTERNAL DICTS & FILTERS
# ===================================================

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# ===================================================
#             ✨ CONFIG LOADED SUCCESSFULLY ✨
# ===================================================
