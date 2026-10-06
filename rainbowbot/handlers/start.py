from aiogram import Router
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_cmd(msg):
    await msg.reply('здрасьте\nя бот')
