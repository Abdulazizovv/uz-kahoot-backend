from django.core.management.base import BaseCommand
import asyncio
from bot.bot import bot


class Command(BaseCommand):
    help = "Show current Telegram webhook info"

    def handle(self, *args, **options):
        async def _info():
            try:
                info = await bot.get_webhook_info()
                return info.model_dump()
            finally:
                await bot.session.close()

        data = asyncio.run(_info())
        self.stdout.write(self.style.SUCCESS("Current webhook info:"))
        for k, v in data.items():
            self.stdout.write(f" - {k}: {v}")
