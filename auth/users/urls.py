from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import telegram_request_otp, telegram_verify_otp

urlpatterns = [
    # Telegram bot auth endpoints
    path('telegram/request-otp/', telegram_request_otp, name='telegram-request-otp'),
    path('telegram/verify-otp/', telegram_verify_otp, name='telegram-verify-otp'),
    
    # JWT token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
