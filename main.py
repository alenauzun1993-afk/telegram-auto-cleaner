import asyncio
import os
import logging
from datetime import date
from collections import defaultdict
from aiogram import Bot, Dispatcher
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Лимиты сообщений в день для топиков {topic_id: max_messages}
TOPIC_LIMITS = {
    5: 2,  # Барахолка
    3: 1,  # Вторая тема (ID: 3)
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
    # Пропускаем сервисные сообщения Telegram и авторепосты
    if not message.from_user or message.is_automatic_forward:
        return

    topic_id = message.message_thread_id
    user_id = message.from_user.id
    today_str = date.today().isoformat()

    # 1. Проверка суточного лимита сообщений
    if topic_id in TOPIC_LIMITS:
        max_allowed = TOPIC_LIMITS[topic_id]
        key = (user_id, topic_id, today_str)
        
        if user_message_counts[key] >= max_allowed:
            # Превышен лимит — мгновенно удаляем сообщение
            try:
                await message.delete()
                # Отправляем временное предупреждение
                warning = await message.answer(
                    f"⚠️ {message.from_user.mention_html()}, лимит сообщений на сегодня в этом топике ({max_allowed} в день) исчерпан. Сообщение удалено.",
                    parse_mode="HTML"
                )
                # Удаляем предупреждение через 12 секунд
                await asyncio.sleep(12)
                await warning.delete()
            except Exception as e:
                logging.error(f"Ошибка при удалении превышенного сообщения: {e}")
            return
        else:
            # Лимит не превышен — увеличиваем счетчик пользователя на сегодня
            user_message_counts[key] += 1

    # 2. Автоудаление через 48 часов (для Барахолки)
    if topic_id in CLEANER_TOPICS:
        await asyncio.sleep(DELETE_DELAY)
        try:
            await message.delete()
            logging.info(f"Удалено сообщение {message.message_id} из топика {topic_id} по истечении 48 часов")
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение по таймеру: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
