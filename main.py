import os
import asyncio
from aiogram import Bot, Dispatcher, types

# Бот берет токен из настроек Render
API_TOKEN = os.getenv("BOT_TOKEN")
# ID темы "Барахолка" или "Услуги" (из ссылки t.me/c/4307605011/3 это цифра 3)
# Если оставить None, будет удалять во ВСЕХ темах
TARGET_TOPIC_ID = None  

# Время жизни сообщения (48 часов = 172800 секунд)
DELETE_DELAY = 172800 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def auto_delete_messages(message: types.Message):
    # Если указана конкретная тема, проверяем ее ID
    if TARGET_TOPIC_ID is not None and message.message_thread_id != TARGET_TOPIC_ID:
        return

    # Ждем 48 часов
    await asyncio.sleep(DELETE_DELAY)
    try:
        await message.delete()
    except Exception as e:
        print(f"Ошибка удаления: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
