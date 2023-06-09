import altron
import os

from random import choice

from pymongo import MongoClient

from pyrogram import Client, filters, idle
from pyrogram.types import Message


API_ID = os.environ.get("API_ID", "25981592")
API_HASH = os.environ.get("API_HASH", "709f3c9d34d83873d3c7e76cdd75b866")
STRING = os.environ.get("STRING", None)
OWNER_ID = os.environ.get("OWNER_ID", "5518687442")
MONGO_URL = os.environ.get("MONGO_URL", None)


bot = Client(STRING, API_ID, API_HASH)
_altClient = MongoClient(MONGO_URL)
chatai = _altClient["AltChatbot"]["WordDb"]
chats_col = _altClient["AltChatbot"]["Chats"]


async def is_admins(chat_id: int):
    return [
        member.user.id
        async for member in bot.iter_chat_members(chat_id, filter="administrators")
    ]


@bot.on_message(filters.command("chatbot", prefixes=["/", ".", "?", "-"]) & filters.group & ~filters.edited)
async def chatbot(_, message: Message):
    if (len(message.command) > 1) and (message.command[1].lower() == "on"):
        if message.from_user:
            user = message.from_user.id
            chat_id = message.chat.id
            if user not in (await is_admins(chat_id)):
                return await message.reply_text("You are not an admin.")
        is_alt = chats_col.find_one({"_id": message.chat.id})
        if is_alt:           
            await message.reply_text(f"Chatbot Is Already Enabled")
        else:
            chats_col.insert_one({"_id": message.chat.id})
            await message.reply_text(f"ChatBot Is Enable!")

    elif (len(message.command) > 1) and (message.command[1].lower() == "off"):
        if message.from_user:
            user = message.from_user.id
            chat_id = message.chat.id
            if user not in (await is_admins(chat_id)):
                return await message.reply_text("You are not an admin.")
        is_alt = chats_col.find_one({"_id": message.chat.id})
        if is_alt:
            chats_col.delete_one({"_id": message.chat.id})
            await message.reply_text(f"Chatbot Disabled!")
        else:
            await message.reply_text(f"ChatBot Is Already Disabled")
    
    else:
        await message.reply_text(f"**Usage:**\n/chatbot [on|off] only group")


@bot.on_message((filters.text | filters.sticker) & filters.group & ~filters.edited & ~filters.bot)
async def altai(_, message: Message):
    if message.reply_to_message:
        is_alt = chats_col.find_one({"_id": message.chat.id})                           
        if message.reply_to_message.from_user.is_self: 
            if not is_alt:                   
                await bot.send_chat_action(message.chat.id, "typing")
                K = []  
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})      
                if k:       
                    for x in is_chat:
                        K.append(x['text'])
                    try:      
                        hey = choice(K)
                    except:
                        hey = k["text"]
                    is_text = chatai.find_one({"text": hey})
                    if is_text['check'] == "sticker":
                        await message.reply_sticker(hey)
                    else:
                        await message.reply_text(hey)
        else:          
            if message.sticker:
                is_chat = chatai.find_one({"word": message.reply_to_message.text, "id": message.sticker.file_unique_id})
                if not is_chat:
                    chatai.insert_one({"word": message.reply_to_message.text, "text": message.sticker.file_id, "check": "sticker", "id": message.sticker.file_unique_id})
            elif message.text:                 
                is_chat = chatai.find_one({"word": message.reply_to_message.text, "text": message.text})                 
                if not is_chat:
                    chatai.insert_one({"word": message.reply_to_message.text, "text": message.text, "check": "none"})    

    else:
        is_alt = chats_col.find_one({"_id": message.chat.id})
        if not is_alt:
            await bot.send_chat_action(message.chat.id, "typing")
            K = []
            is_chat = chatai.find({"word": message.text})
            k = chatai.find_one({"word": message.text})
            if k:
                for x in is_chat:
                    K.append(x['text'])    
                try:      
                    hey = choice(K)
                except:
                    hey = k["text"]
                is_text = chatai.find_one({"text": hey})
                if is_text['check'] == "sticker":
                    await message.reply_sticker(hey)
                else:
                    await message.reply_text(hey)


@bot.on_message((filters.text | filters.sticker) & filters.private & ~filters.edited & ~filters.bot)
async def altprivate(_, message: Message):
    if message.reply_to_message:    
        if message.reply_to_message.from_user.is_self:                    
            await bot.send_chat_action(message.chat.id, "typing")
            K = []  
            is_chat = chatai.find({"word": message.text})                 
            for x in is_chat:
                K.append(x['text'])
            try:
                hey = choice(K)
                is_text = chatai.find_one({"text": hey})
                if is_text['check'] == "sticker":
                    await message.reply_sticker(hey)
                else:
                    await message.reply_text(hey)
            except:
                pass

    else: 
        await bot.send_chat_action(message.chat.id, "typing")
        K = []  
        is_chat = chatai.find({"word": message.text})                 
        for x in is_chat:
            K.append(x['text'])
        try:      
            hey = choice(K)
            is_text = chatai.find_one({"text": hey})
            if is_text['check'] == "sticker":
                await message.reply_sticker(hey)
            else:
                await message.reply_text(hey)
        except:
            pass


@bot.on_message(filters.command('gcast') & filters.user(OWNER_ID) & ~filters.edited & ~filters.forwarded)
async def gcast(client: Client, message: Message):
    chat_ids = []
    async for dialog in client.iter_dialogs():
        chat_ids.append(dialog.chat.id)
    
    await altron.gcast(client, message, chat_ids)


print("Your Chatbot Is Ready Now! Join @TheAltron And @AltronChats")

bot.start()
bot.join_chat("TheAltron")
bot.join_chat("AltronChats")
idle()
bot.stop()
