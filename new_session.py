import asyncio
from pyrogram import Client

api_id = 20342362
api_hash = "967046232d4fd5ad623f49fdba90592d"


async def main():
    async with Client("chat_cotrol", api_id, api_hash) as app:
        await app.send_message("me", "Greetings from **Pyrogram**!")


asyncio.run(main())