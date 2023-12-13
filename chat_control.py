import asyncio



from pyrogram import Client

from db.data_base import chats
from db.base import database



async def get_all_activ_chat():
    old_chat = {}
    query = chats.select()
    old_chat_db = await database.fetch_all(query)
    for old_ch in old_chat_db:
        old_chat[old_ch.tg_chat_id] = old_ch
    return old_chat


async def get_actual_chat(app):
    old_chat = await get_all_activ_chat()
    print(old_chat)
    async for dialog in app.get_dialogs():
        
        chat = dialog.chat
        print(chat.id)
        old = old_chat.get(str(chat.id))
        if old is not None:
            print("old is not None")
            if chat.permissions is not None:
                send_messager = chat.permissions.can_send_messages
            else:
                send_messager = False
            
            value = {
                'name': f'{chat.title} ({chat.username})',
                'is_writable': send_messager
            }
            query = chats.update().where(
                chats.c.id==old.id,
            ).values(**value)
            await database.execute(query)
            old_chat.pop(str(chat.id))
    


    
async def main():
    await database.connect()
    async with Client("my_prod") as app:
        await get_actual_chat(app)


if __name__ == "__main__":
    asyncio.run(main())
            