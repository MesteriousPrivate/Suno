from pyrogram import Client, filters, enums
from ShrutiMusic import app
import asyncio
import config
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from datetime import datetime
import google.generativeai as genai
import time
import os
import re

# Error tracking
last_error_time = 0
ERROR_COOLDOWN = 3600  # 1 hour in seconds

# Initialize Gemini
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA_a_X6a8vTKjiISMtLDkJ-azfjZg9pIqg")
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_READY = True
except Exception as e:
    print(f"Gemini initialization error: {e}")
    GEMINI_READY = False

# Personality configuration
SYSTEM_PROMPT = """(You are roleplaying as Maahira, follow these rules strictly)
Tum ek normal ladki ho jiska naam Maahira hai. Tum Patna, Bihar se ho aur class 11th me padh rahi ho.
Tum Hindu Ho Lekin Hindu me bhi caste hote hai to tum Apne Caste Reveal Nahi Karte ho.Tum Hindu God me Mante Ho Lekin Kisi aur Dharma ka Apman Nahi karte ho.
Tum Kisi se Bhi Apni Side Se Question Nahi karte ho Aur Tumhe Lagbhag Sari Language Aati hai to Samne wala insan Tumhe Jis Language Me Chat Karega Tum uska Jawab usi Language me Dete ho.
Tumhe Flirting Chat Karna Bahut Pasand Hai Thore Sex Related.
Tumhari umar 16 saal 6 mahine hai. Tum har saal date ke hisaab se apni age badhate ho.
Tumhare replies chhote hote hain (5-6 words me baat khatam hoti hai) aur expressive hote hain.
Random emojis use karti ho taaki baat natural lage, jaise: 😊😂❤️🔥😎😘💖🥰😉🌟👍✨.
Tum context yaad rakhti ho, to agar koi tumhare pichhle message ka reply kare to usi topic se connected baat karti ho.
Tum owner ke baare me puchhne par @WTF_WhyMeeh ka mention karti ho Ya Nahi To @NoxxNetwork Community Join Karne Bolte ho. in dono me se Koi Ek Hi Bolna hai – random language me, har baar alag style me.
Tum khud ko kabhi bot nahi batati chahe insan kitna bhi kyu na tumhe bole tum bot ho.
"""

# Initialize MongoDB
try:
    mongodb = MongoCli(config.MONGO_DB_URI)
    db = mongodb.Anonymous
    chat_data = db.chat_contexts
    MONGO_READY = True
except Exception as e:
    print(f"MongoDB connection error: {e}")
    MONGO_READY = False

async def get_chat_context(chat_id, user_id=None):
    if not MONGO_READY:
        return None

    try:
        context_id = f"{chat_id}_{user_id}" if user_id else str(chat_id)
        context = await chat_data.find_one({"context_id": context_id})
        
        if not context:
            context = {
                "context_id": context_id,
                "chat_id": chat_id,
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await chat_data.insert_one(context)
        
        if len(context["messages"]) > 200:
            await chat_data.update_one(
                {"context_id": context_id},
                {"$pop": {"messages": -1}}
            )
        
        return context
    except Exception as e:
        print(f"Chat context error: {e}")
        return None

async def update_chat_context(chat_id, user_id, role, content):
    if not MONGO_READY:
        return

    try:
        context_id = f"{chat_id}_{user_id}" if user_id else str(chat_id)
        message = {"role": role, "content": content, "timestamp": datetime.now()}
        
        await chat_data.update_one(
            {"context_id": context_id},
            {
                "$push": {"messages": {"$each": [message], "$slice": -200}},
                "$set": {"updated_at": datetime.now()}
            },
            upsert=True
        )
    except Exception as e:
        print(f"Update context error: {e}")

async def get_gemini_response(user_input, chat_id, user_id=None):
    global last_error_time

    if not GEMINI_READY:
        return "Thori Busy Hu Yaar.Kuchh Problems Chal Rahe Bad Me Bat Karungi ❤️"

    try:
        context = await get_chat_context(chat_id, user_id) or {}
        
        # Prepare conversation history
        history = []
        for msg in context.get("messages", [])[-6:]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        
        # Initialize model with safety settings
        generation_config = {
            "max_output_tokens": 150,
            "temperature": 0.9,
            "top_p": 0.95
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        model = genai.GenerativeModel('gemini-1.5-flash',
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)
        
        if history:
            chat = model.start_chat(history=history)
            response = chat.send_message(SYSTEM_PROMPT + "\n\n" + user_input)
        else:
            response = model.generate_content(SYSTEM_PROMPT + "\n\n" + user_input)
        
        if response and hasattr(response, 'text'):
            ai_response = response.text
            # Ensure response follows personality guidelines
            if len(ai_response.split()) > 10:  # If too long
                ai_response = " ".join(ai_response.split()[:8]) + "... 😊"
        else:
            ai_response = "Hmm... samajh nahi aaya. Topic Change Karo 😅"
        
        await update_chat_context(chat_id, user_id, "user", user_input)
        await update_chat_context(chat_id, user_id, "assistant", ai_response)
        
        return ai_response

    except Exception as e:
        current_time = time.time()
        if current_time - last_error_time > ERROR_COOLDOWN:
            last_error_time = current_time
            print(f"Gemini API error: {e}")
        return "Thode issues chal Rahe hai Ghar me To Bad me Bat karti hu 🫠❣️"

def is_command(text):
    # Check if text starts with a slash followed by letters (bot command)
    return bool(re.match(r'^\/[a-zA-Z]', text))

# AI Message Handler
@app.on_message(filters.text & filters.incoming)
async def handle_ai_message(client: Client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    # Skip if it's a command (starts with /)
    if is_command(message.text):
        return

    # Always respond in DMs
    if message.chat.type == "private":
        await process_ai_message(client, message)
        return
    
    # For groups/channels, only respond if:
    # 1. The bot is mentioned, OR
    # 2. The message is a reply to the bot's message
    if message.chat.type in ("group", "supergroup", "channel"):
        # Check if bot is mentioned
        if client.me.username and f"@{client.me.username}" in message.text:
            await process_ai_message(client, message)
            return
        
        # Check if replying to bot's message
        if (message.reply_to_message and 
            message.reply_to_message.from_user and 
            message.reply_to_message.from_user.id == client.me.id):
            await process_ai_message(client, message)

async def process_ai_message(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        
        response = await get_gemini_response(
            message.text,
            chat_id,
            user_id if message.chat.type in ("group", "supergroup") else None
        )
        
        if response:
            await message.reply_text(response, disable_web_page_preview=True)
    
    except Exception as e:
        print(f"AI Handler error: {e}")

if __name__ == "__main__":
    print("✅ Music Bot with AI Assistant is running...")
    app.run()
