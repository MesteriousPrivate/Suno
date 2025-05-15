from typing import Dict, Union

from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ParseMode

from config import MONGO_DB_URI
from ShrutiMusic import app

mongo = MongoCli(MONGO_DB_URI).Rankings

impdb = mongo.pretender


async def usr_data(chat_id: int, user_id: int) -> bool:
    user = await impdb.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(user)


async def get_userdata(chat_id: int, user_id: int) -> Union[Dict[str, str], None]:
    user = await impdb.find_one({"chat_id": chat_id, "user_id": user_id})
    return user


async def add_userdata(
    chat_id: int, user_id: int, username: str, first_name: str, last_name: str
):
    await impdb.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        },
        upsert=True,
    )


async def check_pretender(chat_id: int) -> bool:
    chat = await impdb.find_one({"chat_id_toggle": chat_id})
    return bool(chat)


async def impo_on(chat_id: int) -> None:
    await impdb.insert_one({"chat_id_toggle": chat_id})


async def impo_off(chat_id: int) -> None:
    await impdb.delete_one({"chat_id_toggle": chat_id})


@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=69)
async def chk_usr(_, message: Message):
    chat_id = message.chat.id
    if message.sender_chat or not await check_pretender(chat_id):
        return
    user_id = message.from_user.id
    user_data = await get_userdata(chat_id, user_id)
    if not user_data:
        await add_userdata(
            chat_id,
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
        return

    usernamebefore = user_data.get("username", "")
    first_name = user_data.get("first_name", "")
    lastname_before = user_data.get("last_name", "")

    msg = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>\n"

    changes = []

    if (
        first_name != message.from_user.first_name
        and lastname_before != message.from_user.last_name
    ):
        changes.append(
            f"Changed her name from <b>{first_name} {lastname_before}</b> to <b>{message.from_user.first_name} {message.from_user.last_name}</b>\n"
        )
    elif first_name != message.from_user.first_name:
        changes.append(
            f"Changed her first name from <b>{first_name}</b> to <b>{message.from_user.first_name}</b>\n"
        )
    elif lastname_before != message.from_user.last_name:
        changes.append(
            f"Changed her last name from <b>{lastname_before}</b> to <b>{message.from_user.last_name}</b>\n"
        )

    if usernamebefore != message.from_user.username:
        changes.append(
            f"Changed her username from @{usernamebefore} to @{message.from_user.username}\n"
        )

    if changes:
        msg += "".join(changes)
        await message.reply_text(msg, parse_mode=ParseMode.HTML)

    await add_userdata(
        chat_id,
        user_id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )


@app.on_message(
    filters.group & filters.command("pretender") & ~filters.bot & ~filters.via_bot
)
async def set_mataa(_, message: Message):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    if message.from_user.id not in admin_ids:
        return
    if len(message.command) == 1:
        return await message.reply("<b>Detected pretender usage:\n/pretender on|off</b>", parse_mode=ParseMode.HTML)
    chat_id = message.chat.id
    if message.command[1] == "on":
        cekset = await check_pretender(chat_id)
        if cekset:
            await message.reply(
                f"Pretender is already enabled for <b>{message.chat.title}</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await impo_on(chat_id)
            await message.reply(
                f"Successfully enabled pretender for <b>{message.chat.title}</b>",
                parse_mode=ParseMode.HTML
            )
    elif message.command[1] == "off":
        cekset = await check_pretender(chat_id)
        if not cekset:
            await message.reply(
                f"Pretender is already disabled for <b>{message.chat.title}</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await impo_off(chat_id)
            await message.reply(
                f"Successfully disabled pretender for <b>{message.chat.title}</b>",
                parse_mode=ParseMode.HTML
            )
    else:
        await message.reply("<b>Detected pretender usage:\n/pretender on|off</b>", parse_mode=ParseMode.HTML)

@app.on_message(
    filters.group & filters.command("checkuser") & ~filters.bot & ~filters.via_bot
)
async def check_user_details(_, message: Message):
    if len(message.command) != 2:
        return await message.reply("<b>Usage:</b> /checkuser &lt;user_id&gt;", parse_mode=ParseMode.HTML)

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply("<b>Invalid user ID. Please provide a numeric ID.</b>", parse_mode=ParseMode.HTML)

    chat_id = message.chat.id

    # Fetch user data from the database
    user_data = await get_userdata(chat_id, user_id)
    if not user_data:
        return await message.reply(f"<b>No data found for user ID:</b> <code>{user_id}</code>", parse_mode=ParseMode.HTML)

    # Extract old data from the database
    old_username = user_data.get("username", "N/A")
    old_first_name = user_data.get("first_name", "N/A")
    old_last_name = user_data.get("last_name", "N/A")

    try:
        # Fetch current data from Telegram
        current_user = await app.get_users(user_id)
        new_username = current_user.username or "N/A"
        new_first_name = current_user.first_name or "N/A"
        new_last_name = current_user.last_name or "N/A"
    except Exception:
        new_username = "N/A (User not found)"
        new_first_name = "N/A (User not found)"
        new_last_name = "N/A (User not found)"

    # Generate response message
    msg = (
        f"<b>User Details:</b>\n"
        f"- <b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<b>Old Data:</b>\n"
        f"- <b>Username:</b> @{old_username}\n"
        f"- <b>First Name:</b> {old_first_name}\n"
        f"- <b>Last Name:</b> {old_last_name}\n\n"
        f"<b>Current Data:</b>\n"
        f"- <b>Username:</b> @{new_username}\n"
        f"- <b>First Name:</b> {new_first_name}\n"
        f"- <b>Last Name:</b> {new_last_name}\n"
    )

    # Check for changes
    changes = []
    if old_username != new_username:
        changes.append(
            f"<b>Username changed:</b> @{old_username} → @{new_username}\n"
        )
    if old_first_name != new_first_name:
        changes.append(
            f"<b>First name changed:</b> {old_first_name} → {new_first_name}\n"
        )
    if old_last_name != new_last_name:
        changes.append(
            f"<b>Last name changed:</b> {old_last_name} → {new_last_name}\n"
        )

    # Add changes to the message
    if changes:
        msg += "\n<b>Changes Detected:</b>\n" + "".join(changes)
    else:
        msg += "\n<b>No changes detected.</b>"

    await message.reply(msg, parse_mode=ParseMode.HTML)


__MODULE__ = "Pretender"
__HELP__ = """
<b>/pretender</b> [on|off] - To turn on or off pretender for your chat
If any user changes her username, name, bot will send message in your chat
"""
