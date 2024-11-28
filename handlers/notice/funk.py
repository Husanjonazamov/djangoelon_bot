import asyncio
from telethon import TelegramClient, events
from utils import env
from services.services import getNotice
from asgiref.sync import sync_to_async
from main.models import Notice

# TelegramClient yaratish
client = TelegramClient(env.PHONE_NUMBER, env.API_ID, env.API_HASH)

# Takrorlanishni olib tashlagan chat_id ro'yxati
chat_ids = list(set([
    -1002202717276, -1002156534133, -1001368447491, -1002318451740, -1002474360096,
    -1002285384904, -1002375234737, -1001696066827, -1001661240991, -1001950144985,
    -1001889067613, -1002225373901, -1001698342886, -1001561994254, -1001661001936,
    -1002036095755, -1002297602082, -1002345459660, -1001995597670, -1002220623140,
    -1002178966866, -1002159005012, -1002206635995, -1001698975338, -1002067577089,
    -1002232778089, -1002247652778, -1002169615850, -1002161701360, -1001927709760,
    -1002083400408, -1002220553035, -1002089458891, -1002068631562, -1002232013574,
    -1002230508278, -1002406606261, -1001934813270, -1002387686287, -1002215121340,
    -1002367286161
]))



# chat_ids = list(set([
#     -1002259911997, -1002288974096
# ]))

last_notice_data = {}

message_counters = {chat_id: 0 for chat_id in chat_ids}
last_sents = {chat_id: False for chat_id in chat_ids}

async def send_notice(notice, chat_id):
    try:
        formatted_description = f"**{notice.descriptions}**"
        await client.send_message(chat_id, formatted_description, parse_mode='Markdown')
        last_sents[chat_id] = True
        print(f"Xabar yuborildi: {chat_id}")
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        last_sents[chat_id] = False

async def send_all_notices(notice):
    tasks = [send_notice(notice, chat_id) for chat_id in chat_ids]
    await asyncio.gather(*tasks)



@client.on(events.NewMessage())
async def handler(event):
    global message_counters, last_sents

    if event.chat_id in chat_ids:  
        if not event.out:  
            notice_list = await sync_to_async(list)(Notice.objects.all()) 
            if notice_list:
                notice = notice_list[0]  

                message_counters[event.chat_id] += 1
                print(f"New message in {event.chat_id}. Count: {message_counters[event.chat_id]}")

                if message_counters[event.chat_id] >= notice.interval and not last_sents[event.chat_id]:
                    await send_notice(notice, event.chat_id)  
                    message_counters[event.chat_id] = 0 
                elif message_counters[event.chat_id] < notice.interval:
                    last_sents[event.chat_id] = False  