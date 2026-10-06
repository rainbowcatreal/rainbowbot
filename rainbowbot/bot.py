'''
тут создаётся бот и запускается
'''

from aiogram import Bot, Dispatcher, enums
from aiogram.client.default import DefaultBotProperties

from .config import TOKEN
from .handlers import router

async def main():
    # создаём бота и диспетчер
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=enums.ParseMode.HTML
        )
    )
    dp = Dispatcher()

    # добавляем единый роутер (НЕ единую россию)
    dp.include_router(router)

    # запускаем
    await dp.start_polling(bot)
