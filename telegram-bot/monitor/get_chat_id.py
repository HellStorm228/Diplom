import asyncio
from telegram import Bot

TOKEN = "8796380258:AAGM0lR-s4FrjdOCdnOMswE0bcvrKhkfR64"

async def main():
    bot = Bot(token=TOKEN)
    updates = await bot.get_updates()

    for update in updates:
        if update.message:
            print(update.message.chat.id)

asyncio.run(main())
