from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from asgiref.sync import async_to_sync

from .serializers import (
    TelegramRequestOTPSerializer,
    TelegramVerifyOTPSerializer,
    TokenResponseSerializer,
    get_tokens_for_user
)
from auth.utils.otp import OTPManager
from apps.botapp.models import BotUser

User = get_user_model()
otp_manager = OTPManager()


@extend_schema(
    tags=['Authentication'],
    summary='Request OTP code via Telegram',
    description='Request a 5-digit OTP code that will be sent to user via Telegram bot. '
                'Rate limited to 1 request per minute.',
    request=TelegramRequestOTPSerializer,
    responses={
        200: OpenApiResponse(
            description='OTP sent successfully',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'success': True,
                        'message': 'OTP kod Telegram botga yuborildi.',
                        'expires_in': 300
                    }
                )
            ]
        ),
        404: OpenApiResponse(
            description='User not found or not registered',
            examples=[
                OpenApiExample(
                    'User not found',
                    value={'error': 'User not found', 'message': "Telegram bot orqali /start buyrug'ini bosing."}
                ),
                OpenApiExample(
                    'Not registered',
                    value={'error': 'User not registered', 'message': "Avval ro'yxatdan o'ting."}
                )
            ]
        ),
        429: OpenApiResponse(
            description='Rate limit exceeded',
            examples=[
                OpenApiExample(
                    'Too many requests',
                    value={
                        'error': 'Too many requests',
                        'message': "Iltimos, 45 soniyadan so'ng qayta urinib ko'ring.",
                        'remaining_seconds': 45
                    }
                )
            ]
        ),
        500: OpenApiResponse(description='Server error')
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_request_otp(request):
    """
    Telegram user_id orqali OTP kod so'rash.
    
    OTP kodni Telegram bot orqali yuborish uchun.
    """
    serializer = TelegramRequestOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = serializer.validated_data['user_id']
    
    # Rate limiting tekshirish
    if not otp_manager.can_request_otp(user_id):
        remaining_time = otp_manager.get_remaining_time(user_id)
        return Response(
            {
                'error': 'Too many requests',
                'message': f'Iltimos, {remaining_time} soniyadan so\'ng qayta urinib ko\'ring.',
                'remaining_seconds': remaining_time
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # BotUser mavjudligini tekshirish
    try:
        bot_user = BotUser.objects.get(user_id=user_id)
    except BotUser.DoesNotExist:
        return Response(
            {'error': 'User not found', 'message': 'Telegram bot orqali /start buyrug\'ini bosing.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # User bog'langanligini tekshirish
    try:
        user = User.objects.get(bot_user=bot_user)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not registered', 'message': 'Avval ro\'yxatdan o\'ting.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # OTP generatsiya qilish
    otp = otp_manager.generate_otp()
    
    # OTP ni Redis ga saqlash
    if not otp_manager.save_otp(user_id, otp):
        return Response(
            {'error': 'Server error', 'message': 'OTP saqlashda xatolik.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # OTP ni Telegram bot orqali yuborish
    from bot.bot import bot
    
    try:
        # Async function ni sync context da ishlatish (Django uchun to'g'ri usul)
        send_message = async_to_sync(bot.send_message)
        send_message(
            chat_id=int(user_id),
            text=f"🔐 Sizning login kodingiz: <code>{otp}</code>\n\n"
                 f"Kod 5 daqiqa davomida amal qiladi.\n"
                 f"Agar siz bu kodni so'ramagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring."
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to send OTP', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response(
        {
            'success': True,
            'message': 'OTP kod Telegram botga yuborildi.',
            'expires_in': 300  # 5 daqiqa
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Authentication'],
    summary='Verify OTP and get JWT tokens',
    description='Verify the OTP code received via Telegram and get JWT access and refresh tokens. '
                'OTP codes are valid for 5 minutes and are deleted after successful verification. '
                'Only the OTP code is required, no user_id needed.',
    request=TelegramVerifyOTPSerializer,
    responses={
        200: OpenApiResponse(
            response=TokenResponseSerializer,
            description='OTP verified successfully, returns JWT tokens',
            examples=[
                OpenApiExample(
                    'Success',
                    value={
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': '123e4567-e89b-12d3-a456-426614174000',
                            'phone_number': '+998901234567',
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'email': 'john@example.com',
                            'user_type': 'student',
                            'phone_verified': True
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description='Invalid or expired OTP',
            examples=[
                OpenApiExample(
                    'Invalid OTP',
                    value={'error': 'Invalid OTP', 'message': "Noto'g'ri yoki muddati o'tgan OTP kod."}
                )
            ]
        ),
        404: OpenApiResponse(description='User not found')
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_verify_otp(request):
    """
    OTP kodni tekshirish va JWT token berish.
    """
    serializer = TelegramVerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    otp = serializer.validated_data['otp']
    
    # OTP ni tekshirish va user_id ni olish
    user_id = otp_manager.verify_otp_by_code(otp)
    
    if not user_id:
        return Response(
            {'error': 'Invalid OTP', 'message': 'Noto\'g\'ri yoki muddati o\'tgan OTP kod.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # BotUser orqali User topish
    try:
        bot_user = BotUser.objects.get(user_id=user_id)
        user = User.objects.get(bot_user=bot_user)
    except (BotUser.DoesNotExist, User.DoesNotExist):
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # JWT tokenlarni yaratish
    tokens = get_tokens_for_user(user)
    
    response_serializer = TokenResponseSerializer(tokens)
    
    return Response(
        response_serializer.data,
        status=status.HTTP_200_OK
    )
