import os
import re
import asyncio
import signal
import hashlib

from sqlalchemy import select, func, distinct
from pyrogram import Client, idle
from pyrogram.enums import ChatType, MessageServiceType
from pyrogram import filters
from pyrogram.handlers import MessageHandler, UserStatusHandler, ChatMemberUpdatedHandler
from pyrogram.types import ChatMemberUpdated

from db.data_base import chats, message_routing, text_data
from db.base import database



api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

app = Client("prond_final", api_id=api_id, api_hash=api_hash)

class Route:
    def __init__(self,  recipient_id,  is_anonym, not_duplicate, prefix) -> None:
        self.recipient_id = recipient_id
        self.is_anonym = is_anonym
        self.not_duplicate =not_duplicate
        self.prefix = prefix


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
                    'name': f'{chat.title} ({chat.username})',
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

async def other_chats_in_user(message):
    chat = message.chat
    if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        search_query = chats.select().where(
            chats.c.tg_chat_id == str(chat.id)
        )
        answer = await database.fetch_one(search_query)
        if answer is None:
            value = {
                'tg_chat_id': str(chat.id),
                'name': f'{chat.title} ({chat.username})',
                'is_writable': False
            }
            query = chats.insert().values(**value)
            await database.execute(query)

def check_phone_number(phone_number):
    result = ''
    number = '0123456789'
    is_number=False
    
    text = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    for y in  text:
        if y in number:
            if not is_number:
                result += ' '
                is_number = True
        else:
            if is_number:
                result += ' '
                is_number = False
        result += y
    print(text)
    match = re.search(r'\b\d{7}\b|\b\d{10}\b|\b\d{11}\b', result )
    if match:
        print('есть телефон')
        return True
    print('нет телефона')
    return False



def not_phone_number(text):
    return not check_phone_number(text)


key_text = {
    '*нет-телефона': not_phone_number,
    '*есть-телефон': check_phone_number
}

def words_control(words, message_text):
    for word in words:
        word = word.strip()
        if word != '':
            word = word.replace(" ", "").lower()
            if word in key_text:
                return key_text[word](message_text)
            if '_' in word:
                wr = word.split('_')
                if all(sub.replace(" ", "").lower() in   message_text.lower() for sub in wr):
                    return True
            elif '-' in word:
                wr = word.replace("-", " ")
                if wr in message_text.lower():
                    return True
            elif word in message_text.lower():
                return True
    return False


def get_short_text(text):
    hash_object = hashlib.md5(text.encode())
    unique_string = hash_object.hexdigest()

    # Возвращаем первые 8 символов для сокращения строки
    return unique_string[:15]



async def get_route(message):
    duplex_control = []
    if message.text is None:
        return []
    result = []
    chat = message.chat
    search_query = select([chats, message_routing]).join(message_routing, chats.c.id == message_routing.c.sender_id).where(
        chats.c.tg_chat_id == str(chat.id)
    )
    answer = await database.fetch_all(search_query)
   
    for ans in answer:
        
        if ans.recipient_id in duplex_control:
            continue
        triggers = ans.trigger_words.split(',')
        stop_words = ans.exclude_words.split(',')
        prefix = ans.prefix
        if words_control(words=stop_words, message_text=message.text):
            continue
        if words_control(words=triggers, message_text=message.text):
            duplex_control.append(ans.recipient_id)
            result.append(
                Route(
                    recipient_id=ans.recipient_id,
                    is_anonym=ans.is_anonym,
                    not_duplicate=ans.not_duplicate,
                    prefix=prefix
                )
            )
    return result
            


#MessageServiceType.NEW_CHAT_MEMBERS
async def main_handler(client, message):
    chat = message.chat
    if hasattr(message, 'service'):
        await actual_chat_control(message)
    
    await other_chats_in_user(message)
    route = await get_route(message)
    for r in route:
        query = chats.select().where(
            chats.c.id == r.recipient_id
        )
        answer = await database.fetch_one(query)
        text = ''
        if r.prefix is not None:
            text = r.prefix
        chat_id = int(answer.tg_chat_id)
        if r.not_duplicate:
            short_text = get_short_text(message.text)
            print(short_text)
            query = text_data.select().where(
                text_data.c.message_text==short_text
            )
            ans = await database.fetch_one(query)
            print('answer',ans)
            if ans is not None:
                return
            value = {
                'chat_id': r.recipient_id,
                'message_text': short_text
            }
            query = text_data.insert().values(**value)
            await database.execute(query)
        if r.is_anonym:
            await client.send_message(chat_id, str(text) +'\n'+ message.text)
        else:
            if r.prefix is not None and r.prefix != '':
                await client.send_message(chat_id, r.prefix)
            await client.forward_messages(chat_id, int(chat.id), message.id)
            await asyncio.sleep(0,5)
            await client.send_message(chat_id, f'источник: {chat.title} ({chat.username})', reply_to_message_id=message.id)
    

    
    if message.service==MessageServiceType.LEFT_CHAT_MEMBERS:
        print(f'')
    
        print(f'Новый чат {message.service}')
    
    
    print(f"новое сообщение из чата {message.id}")
    print(message.chat.id)


async def chat_member(client, update: ChatMemberUpdated):
    print("chat_member")
    print(update)



#app.add_handler(MessageHandler(main_handler))
#app.add_handler(ChatMemberUpdatedHandler(chat_member))
#app.run()


async def main():
    await database.connect()
    app = Client("prond_final", api_id=api_id, api_hash=api_hash)
    app.add_handler(MessageHandler(main_handler))
    app.add_handler(ChatMemberUpdatedHandler(chat_member))
    await app.start()
    await idle()


asyncio.run(main())