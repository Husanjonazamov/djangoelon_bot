from telethon import TelegramClient, events
from utils import env
from services.services import getNotice
from asgiref.sync import sync_to_async
from main.models import Notice

client = TelegramClient(env.PHONE_NUMBER, env.API_ID, env.API_HASH)

chat_ids = [
    -1002264446732, -1002037632361,
]

message_counters = {chat_id: 0 for chat_id in chat_ids}
last_sents = {chat_id: False for chat_id in chat_ids}

last_notice_data = {}


async def send_notice(notice, chat_id):
    global last_sent
    try:
        await client.send_message(chat_id, notice.descriptions, parse_mode='markdown')
        last_sents[chat_id] = True 
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        last_sents[chat_id] = False  

@client.on(events.NewMessage())  
async def handler(event):
    global message_counters, last_sents
    if event.chat_id in chat_ids:  # Agar xabar kutilgan guruhdan kelsa
        if not event.out:  # Agar xabar tashqaridan kelgan bo'lsa
            notices = await sync_to_async(getNotice)()  
            if notices:
                message_counters[event.chat_id] += 1  # Guruhdagi xabar sonini oshir
                print(f"New message received in chat {event.chat_id}. Current count: {message_counters[event.chat_id]}")

                notice_list = await sync_to_async(list)(Notice.objects.all())
                
                if notice_list:  
                    notice = notice_list[0]  # Dastlabki notice ni olish

                    # Har bir guruh uchun xabar yuborish shartini tekshirish
                    if message_counters[event.chat_id] >= notice.interval and not last_sents[event.chat_id]:
                        await send_notice(notice, event.chat_id)
                        message_counters[event.chat_id] = 0  # Xabar yuborilgandan keyin hisobni tozalash

                    elif message_counters[event.chat_id] < notice.interval:
                        last_sents[event.chat_id] = False  # Shart bajarilmasa, xabar yuborilmasin

