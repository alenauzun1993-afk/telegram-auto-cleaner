import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID топика «Барахолка»
ALLOWED_TOPICS = [5]

DELETE_DELAY = 48 * 3600  # 48 часов в секундах

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    # Проверяем ID топика
    topic_id = message.message_thread_id
    
    # Если сообщение отправлено в «Барахолку» (ID: 5)
    if topic_id in ALLOWED_TOPICS:
        await asyncio.sleep(DELETE_DELAY)
        try:
            await message.delete()
            logging.info(f"Удалено сообщение {message.message_id} из топика {topic_id}")
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
