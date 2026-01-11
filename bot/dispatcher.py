from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from .routers import register_routers
from .data.config import REDIS_HOST, REDIS_PORT, REDIS_DB


def create_dispatcher() -> Dispatcher:
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    register_routers(dp)
    return dp


# A global dispatcher instance (can be imported where needed)
dp = create_dispatcher()
