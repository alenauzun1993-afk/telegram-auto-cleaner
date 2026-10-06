import asyncio
import os
import logging
from datetime import date
from collections import defaultdict
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiohttp import web

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Лимиты сообщений в день для топиков {topic_id: max_messages}
TOPIC_LIMITS = {
    5: 2,  # Барахолка
    3: 1,  # Вторая тема
    7: 1   # Недвижимость
}

# Топики с автоудалением через 48 часов
CLEANER_TOPICS = [5]
DELETE_DELAY = 48 * 3600  # 48 часов в секундах

# Хранилище счетчиков сообщений: {(user_id, topic_id, date_str): count}
user_message_counts = defaultdict(int)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    if not message.from_user or message.is_automatic_forward:
        return

    topic_id = message.message_thread_id
    user_id = message.from_user.id
    today_str = date.today().isoformat()

    # 1. Проверка суточного лимита
    if topic_id in TOPIC_LIMITS:
        max_allowed = TOPIC_LIMITS[topic_id]
        key = (user_id, topic_id, today_str)
        
        if user_message_counts[key] >= max_allowed:
            try:
                await message.delete()
                warning = await message.answer(
                    f"⚠️ {message.from_user.mention_html()}, лимит сообщений на сегодня в этом топике ({max_allowed} в день) исчерпан. Сообщение удалено.",
                    parse_mode="HTML"
                )
                await asyncio.sleep(12)
                await warning.delete()
            except Exception as e:
                logging.error(f"Ошибка при удалении: {e}")
            return
        else:
            user_message_counts[key] += 1

    # 2. Автоудаление через 48 часов
    if topic_id in CLEANER_TOPICS:
        await asyncio.sleep(DELETE_DELAY)
        try:
            await message.delete()
            logging.info(f"Удалено сообщение {message.message_id} из топика {topic_id}")
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение по таймеру: {e}")

# Микро веб-сервер для удержания порта на Render (Free Web Service)
async def handle_web(request):
    return web.Response(text="Bot is active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
