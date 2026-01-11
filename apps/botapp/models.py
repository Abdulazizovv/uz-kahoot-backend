from django.db import models
from django.conf import settings
from apps.common.models import BaseModel


class BotUser(BaseModel):
    user_id = models.CharField(max_length=100, unique=True, verbose_name="Telegram User ID")
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Familiya")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    language_code = models.CharField(max_length=10, null=True, blank=True, verbose_name="Til kodi")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="Telefon raqami")
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    is_bot = models.BooleanField(default=False, verbose_name="Bot")
    last_interaction = models.DateTimeField(auto_now=True, verbose_name="Oxirgi muloqot")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})" if self.username else f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Bot foydalanuvchisi"
        verbose_name_plural = "Bot foydalanuvchilari"