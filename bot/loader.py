from aiogram import Bot, types
from bot.dispatcher import create_dispatcher
from bot.data import config
from bot.utils.db_api.db import DB


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = create_dispatcher()
db = DB()


