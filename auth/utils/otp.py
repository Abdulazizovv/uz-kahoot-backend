import random
import redis
from django.conf import settings


class OTPManager:
    """OTP kodlarni boshqarish uchun utility class"""
    
    def __init__(self):
        redis_host = getattr(settings, 'REDIS_HOST', 'redis')
        redis_port = getattr(settings, 'REDIS_PORT', 6379)
        redis_db = getattr(settings, 'REDIS_DB', 0)
        
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.otp_expiry = 300  # 5 daqiqa (sekundda)
        self.rate_limit_expiry = 60  # 1 daqiqa
    
    def generate_otp(self) -> str:
        """5 xonali tasodifiy OTP kod yaratadi"""
        return str(random.randint(10000, 99999))
    
    def save_otp(self, user_id: str, otp: str) -> bool:
        """OTP ni Redis ga saqlaydi (user_id va otp_code ga bog'laydi)"""
        key = f"otp:{user_id}"
        reverse_key = f"otp_code:{otp}"
        try:
            # user_id orqali OTP topish uchun
            self.redis_client.setex(key, self.otp_expiry, otp)
            # OTP orqali user_id topish uchun (reverse mapping)
            self.redis_client.setex(reverse_key, self.otp_expiry, user_id)
            return True
        except Exception as e:
            print(f"Error saving OTP: {e}")
            return False
    
    def verify_otp(self, user_id: str, otp: str) -> bool:
        """OTP ni tekshiradi (user_id bilan)"""
        key = f"otp:{user_id}"
        stored_otp = self.redis_client.get(key)
        
        if stored_otp and stored_otp == otp:
            # OTP to'g'ri - barcha keylarni o'chirish
            self.redis_client.delete(key)
            self.redis_client.delete(f"otp_code:{otp}")
            return True
        return False
    
    def verify_otp_by_code(self, otp: str) -> str | None:
        """OTP kodni tekshiradi va user_id ni qaytaradi"""
        reverse_key = f"otp_code:{otp}"
        user_id = self.redis_client.get(reverse_key)
        
        if user_id:
            # OTP to'g'ri - barcha keylarni o'chirish
            self.redis_client.delete(reverse_key)
            self.redis_client.delete(f"otp:{user_id}")
            return user_id
        return None
    
    def can_request_otp(self, user_id: str) -> bool:
        """Rate limiting: 1 daqiqada faqat 1 marta OTP so'rash mumkin"""
        rate_key = f"otp_rate:{user_id}"
        
        if self.redis_client.exists(rate_key):
            return False
        
        # Rate limit qo'yish
        self.redis_client.setex(rate_key, self.rate_limit_expiry, "1")
        return True
    
    def get_remaining_time(self, user_id: str) -> int:
        """Rate limit qolgan vaqtni qaytaradi (sekundda)"""
        rate_key = f"otp_rate:{user_id}"
        ttl = self.redis_client.ttl(rate_key)
        return ttl if ttl > 0 else 0
