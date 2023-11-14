
import asyncio
import signal

from sqlalchemy import select, func, distinct
from pyrogram import Client, idle
from pyrogram.enums import ChatType, MessageServiceType
from pyrogram import filters
from pyrogram.handlers import MessageHandler, UserStatusHandler, ChatMemberUpdatedHandler
from pyrogram.types import ChatMemberUpdated

from db.data_base import chats, message_routing
from db.base import database




api_id = 20342362
api_hash = "967046232d4fd5ad623f49fdba90592d"

app = Client("my_account", api_id=api_id, api_hash=api_hash)




async def actual_chat_control(message):
    chat = message.chat
    if message.service in (MessageServiceType.NEW_CHAT_MEMBERS, MessageServiceType.GROUP_CHAT_CREATED):
        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            search_query = chats.select().where(
                chats.c.tg_chat_id == str(chat.id)
            )
            answer = await database.fetch_one(search_query)
            if answer is None:
                send_messager = chat.permissions.can_send_messages
                value = {
                    'tg_chat_id': str(chat.id),
                    'name': chat.title,
                    'is_writable': send_messager
                }
                query = chats.insert().values(**value)
                await database.execute(query)
    elif message.service in (MessageServiceType.LEFT_CHAT_MEMBERS,):
        search_query = chats.select().where(
            chats.c.tg_chat_id == str(chat.id)
        )
        answer = await database.fetch_one(search_query)
        if answer is not None:
            query = chats.delete().where(
                chats.c.tg_chat_id == str(chat.id)
            )
            await database.execute(query)

'''
async def get_route(message):
    if message.text is None:
        return []
    result = []
    chat = message.chat
    search_query = select([chats, message_routing]).join(message_routing, chats.c.id == message_routing.c.sender_id).where(
        chats.c.tg_chat_id == str(chat.id)
    )
    answer = await database.fetch_all(search_query)
    for ans in answer:
        if ans.recipient_id in result:
            continue
        triggers = ans.trigger_words.lower().replace(" ", "").split(',')
        for trigger in triggers:
            if '+' in trigger:
                trigger.replace("+", " ")
            if trigger in message.text.lower():
                result.append(ans.recipient_id)
    return result'''


async def get_route(message):
    if message.text is None:
        return []
    result = []
    chat = message.chat
    search_query = select([chats, message_routing]).join(message_routing, chats.c.id == message_routing.c.sender_id).where(
        chats.c.tg_chat_id == str(chat.id)
    )
    answer = await database.fetch_all(search_query)
    for ans in answer:
        if ans.recipient_id in result:
            continue
        triggers = ans.trigger_words.split(',')
        for trigger in triggers:
            if trigger == '' or trigger ==' ':
                continue
            trigger = trigger.replace(" ", "").lower()
            trigger = trigger.strip()
            print('trigger', trigger, message.text)
            if '_' in trigger:
                tg = trigger.split('_')
                print('tg', tg)
                if all(sub.replace(" ", "").lower() in  message.text.lower() for sub in tg):
                    result.append(ans.recipient_id)
            elif trigger in message.text.lower():
                result.append(ans.recipient_id)
    print(result)
    return result
            


#MessageServiceType.NEW_CHAT_MEMBERS
async def my_handler(client, message):
    chat = message.chat
    if hasattr(message, 'service'):
        await actual_chat_control(message)
    route = await get_route(message)
    for r in route:
        query = chats.select().where(
            chats.c.id == r
        )
        answer = await database.fetch_one(query)
        chat_id = int(answer.tg_chat_id)
        
        await client.forward_messages(chat_id, int(chat.id), message.id)

        await asyncio.sleep(0,5)
        await client.send_message(chat_id, chat.title, reply_to_message_id=message.id)
    

    print(message)
    
    if message.service==MessageServiceType.LEFT_CHAT_MEMBERS:
        print(f'')
    
        print(f'Новый чат {message.service}')
    
    
    print(f"новое сообщение из чата {message.id}")
    print(message.chat.id)


async def chat_member(client, chat_member_updated):
    print(chat_member_updated)



#app.add_handler(MessageHandler(my_handler))
#app.add_handler(ChatMemberUpdatedHandler(chat_member))
#app.run()


async def main():
    await database.connect()
    app = Client("my_account", api_id=api_id, api_hash=api_hash)
    app.add_handler(MessageHandler(my_handler))
    app.add_handler(ChatMemberUpdatedHandler(chat_member))
    await app.start()
    await idle()


asyncio.run(main())
