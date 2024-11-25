from telethon import TelegramClient, events
from utils import env
from services.services import getNotice
from asgiref.sync import sync_to_async
from main.models import Notice

# TelegramClient ni yaratish
client = TelegramClient(env.PHONE_NUMBER, env.API_ID, env.API_HASH)

chat_ids = [
    -1002202717276, -1002156534133, -1001368447491, -1002318451740, -1002474360096,
    -1002285384904, -1002375234737, -1001696066827, -1001661240991, -1001950144985,
    -1001889067613, -1002225373901, -1001698342886, -1001561994254, -1001661001936,
    -1002036095755, -1002297602082, -1002345459660, -1001995597670, -1002220623140,
    -1002178966866, -1002159005012, -1002206635995, -1001698975338, -1002067577089,
    -1002232778089, -1002247652778, -1002169615850, -1002161701360, -1001927709760,
    -1002083400408, -1002220553035, -1002089458891, -1002068631562, -1002232013574,
    -1002230508278, -1002406606261, -1001934813270, -1002387686287, -1002215121340
]


# chat_ids = [
#     -1002259911997,
# ]

message_counters = {chat_id: 0 for chat_id in chat_ids}
last_sents = {chat_id: False for chat_id in chat_ids}
last_notice_data = {}


# Xabar yuborish uchun funksiya
async def send_notice(notice, chat_id):
    try:
        # Matnni <strong></strong> teglariga o'rab olish
        formatted_description = f"**{notice.descriptions}**"

        # Xabarni yuborish
        await client.send_message(chat_id, formatted_description, parse_mode='Markdown')
        last_sents[chat_id] = True  
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        last_sents[chat_id] = False



@client.on(events.NewMessage())  
async def handler(event):
    global message_counters, last_sents
    if event.chat_id in chat_ids: 
        if not event.out: 
            notices = await sync_to_async(getNotice)()  
            if notices:
                message_counters[event.chat_id] += 1  
                print(f"New message received in chat {event.chat_id}. Current count: {message_counters[event.chat_id]}")

                notice_list = await sync_to_async(list)(Notice.objects.all())  
                
                if notice_list:  
                    notice = notice_list[0]  

                    if message_counters[event.chat_id] >= notice.interval and not last_sents[event.chat_id]:
                        await send_notice(notice, event.chat_id) 
                        message_counters[event.chat_id] = 0  

                    elif message_counters[event.chat_id] < notice.interval:
                        last_sents[event.chat_id] = False  

