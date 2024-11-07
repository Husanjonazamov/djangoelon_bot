from telethon import TelegramClient, events
from utils import env
from services.services import getNotice
from asgiref.sync import sync_to_async

client = TelegramClient(env.PHONE_NUMBER, env.API_ID, env.API_HASH)

chat_id = -1002264446732
last_sent = False
last_notice_data = {}


async def send_notice(notice):
    global last_sent
    await client.send_message(chat_id, notice['descriptions'])
    last_sent = True
    

@client.on(events.NewMessage(chats=chat_id))
async def handler(event):
    global last_sent
    if not event.out and not last_sent:
        notices = await sync_to_async(getNotice)()  
        if notices:  
            await send_notice(notices[0]) 
    elif not event.out: 
        last_sent = False  
