from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import os
import sys
import django
import re

# Django settings ni sozlash
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.botapp.models import BotUser
from auth.users.models import User
from auth.utils.otp import OTPManager
from bot.states.registration_state import Registration
from bot.keyboards.default.registration import get_fullname_keyboard, get_phone_keyboard

user_router = Router(name="user-router")
otp_manager = OTPManager()
_PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def _extract_login_phone(raw_text: str) -> str | None:
    raw_text = (raw_text or "").strip()
    if not raw_text.startswith("/login"):
        return None

    first, *rest = raw_text.split(maxsplit=1)
    remainder = ""

    if first == "/login" or first.startswith("/login@"):
        remainder = (rest[0] if rest else "").strip()
    else:
        # Handles cases like: "/login+998..." or "/login@botname+998..."
        after = first[len("/login") :]
        if after.startswith("@"):
            bot_and_more = after[1:]
            m = re.search(r"[+0-9]", bot_and_more)
            remainder = bot_and_more[m.start() :] if m else ""
        else:
            remainder = after
        if rest:
            remainder = f"{remainder} {rest[0]}".strip()

    if not remainder:
        return None

    candidate = remainder.split()[0].replace(" ", "")
    if not _PHONE_RE.fullmatch(candidate):
        return ""

    return candidate if candidate.startswith("+") else f"+{candidate}"


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    /start buyrug'i. User ro'yxatdan o'tgan yoki o'tmaganligini tekshiradi.
    """
    user_id = str(message.from_user.id)
    
    # BotUser mavjudligini tekshirish
    try:
        bot_user = await BotUser.objects.aget(user_id=user_id)
        
        # Agar user bog'langan bo'lsa
        if await User.objects.filter(bot_user=bot_user).aexists():
            await message.answer(
                f"Assalomu alaykum, {message.from_user.full_name}!\n"
                "Siz allaqachon ro'yxatdan o'tgansiz. 🎉",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            # BotUser bor lekin User bog'lanmagan
            await start_registration(message, state)
    except BotUser.DoesNotExist:
        # BotUser ham yo'q - yangi foydalanuvchi
        # BotUser yaratish
        await BotUser.objects.acreate(
            user_id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name or "",
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )
        await start_registration(message, state)


async def start_registration(message: Message, state: FSMContext):
    """
    Ro'yxatdan o'tishni boshlaydi.
    """
    keyboard = get_fullname_keyboard(
        message.from_user.first_name,
        message.from_user.last_name or ""
    )
    
    await message.answer(
        "📝 Ro'yxatdan o'tish uchun ism va familiyangizni kiriting:\n\n"
        "Yoki Telegram profilingizdagi ism-familiyani qabul qilish uchun pastdagi tugmani bosing.",
        reply_markup=keyboard
    )
    await state.set_state(Registration.full_name)


@user_router.message(Registration.full_name, F.text)
async def process_full_name(message: Message, state: FSMContext):
    """
    Ism va familyani qabul qiladi.
    """
    full_name = message.text.strip()
    
    if len(full_name) < 3:
        await message.answer("❌ Ism va familiya juda qisqa. Iltimos, qaytadan kiriting:")
        return
    
    # Statega saqlash
    await state.update_data(full_name=full_name)
    
    # Telefon raqam so'rash
    keyboard = get_phone_keyboard()
    await message.answer(
        "📱 Telefon raqamingizni yuboring:\n\n"
        "Pastdagi tugmani bosib, telefon raqamingizni yuboring.",
        reply_markup=keyboard
    )
    await state.set_state(Registration.phone_number)


@user_router.message(Registration.phone_number, F.contact)
async def process_phone_number(message: Message, state: FSMContext):
    """
    Telefon raqamni qabul qiladi va ro'yxatdan o'tkazadi.
    """
    phone_number = message.contact.phone_number
    
    # + qo'shish agar yo'q bo'lsa
    if not phone_number.startswith('+'):
        phone_number = f'+{phone_number}'
    
    # State dan ma'lumotlarni olish
    data = await state.get_data()
    full_name = data.get('full_name', '')
    
    # Ism va familiyani ajratish
    name_parts = full_name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    user_id = str(message.from_user.id)
    
    try:
        bot_user = await BotUser.objects.aget(user_id=user_id)
        
        # Telefon raqam BotUser ga saqlash
        bot_user.phone_number = phone_number
        await bot_user.asave()
        
        # Telefon raqam bilan user mavjudligini tekshirish
        try:
            user = await User.objects.aget(phone_number=phone_number)
            
            # Mavjud userga BotUser ni bog'lash
            user.bot_user = bot_user
            await user.asave()
            
            await message.answer(
                f"✅ Sizning hisobingiz topildi va Telegram botga bog'landi!\n\n"
                f"👤 Ism: {user.get_full_name()}\n"
                f"📱 Telefon: {user.phone_number}",
                reply_markup=ReplyKeyboardRemove()
            )
            
        except User.DoesNotExist:
            # User mavjud emas - yangi user yaratish
            user = await User.objects.acreate(
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                user_type='student',
                phone_verified=True,
                bot_user=bot_user
            )
            
            await message.answer(
                f"✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n"
                f"👤 Ism: {user.get_full_name()}\n"
                f"📱 Telefon: {user.phone_number}",
                reply_markup=ReplyKeyboardRemove()
            )
        
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f"❌ Xatolik yuz berdi: {str(e)}\n\n"
            "Iltimos, keyinroq qayta urinib ko'ring.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()


@user_router.message(Registration.phone_number)
async def process_phone_invalid(message: Message):
    """
    Agar telefon raqam contact orqali yuborilmagan bo'lsa.
    """
    await message.answer(
        "❌ Iltimos, telefon raqamni pastdagi tugma orqali yuboring!\n\n"
        "Qo'lda kiritish mumkin emas.",
        reply_markup=get_phone_keyboard()
    )


@user_router.message(StateFilter(Registration.full_name, Registration.phone_number))
async def process_invalid_state(message: Message):
    """
    Agar ro'yxatdan o'tish jarayonida noto'g'ri buyruq yuborilsa.
    """
    await message.answer(
        "❌ Iltimos, avval ro'yxatdan o'tishni yakunlang!\n\n"
        "Yuqoridagi ko'rsatmalarga amal qiling."
    )


@user_router.message(Command("help"))
async def cmd_help(message: Message):
    text = [
        "Commands:",
        "/start - Start the bot",
        "/login - Tizimga kirish uchun OTP olish",
        "/login +998901234567 - (faqat superuser) istalgan hisob uchun OTP olish",
        "/help - This help message",
    ]
    await message.answer("\n".join(text))


@user_router.message(Command("login"))
async def cmd_login(message: Message, command: CommandObject | None = None):
    """
    Tizimga kirish uchun OTP kod so'rash.
    """
    user_id = str(message.from_user.id)

    # Superuser flow: /login <phone_number>
    target_phone = ((command.args or "").strip().split()[0] if command and command.args else "")
    if target_phone and target_phone.startswith("@"):
        # Defensive: ignore accidental mentions
        target_phone = ""
    if target_phone:
        target_phone = target_phone.replace(" ", "")
        if not target_phone.startswith("+"):
            target_phone = f"+{target_phone}"
        if not _PHONE_RE.fullmatch(target_phone):
            target_phone = ""

    extracted = _extract_login_phone(message.text or message.caption or "")
    if not target_phone and extracted is not None:
        # extracted == "" means user provided an invalid phone argument
        target_phone = extracted

    if target_phone == "":
        await message.answer(
            "❌ Telefon raqam formati noto'g'ri.\n\n"
            "Masalan: /login +998901234567"
        )
        return

    if target_phone:

        # Requester must be a linked superuser
        try:
            requester_bot_user = await BotUser.objects.aget(user_id=user_id)
            requester_is_superuser = await User.objects.filter(
                bot_user=requester_bot_user, is_superuser=True, is_active=True
            ).aexists()
        except BotUser.DoesNotExist:
            requester_is_superuser = False

        if not requester_is_superuser:
            await message.answer(
                "❌ Sizda bu buyruqdan foydalanish uchun ruxsat yo'q.\n\n"
                "O'zingiz uchun kod olish: /login"
            )
            return

        # Find target user by phone number (with/without leading +)
        phone_without_plus = target_phone.lstrip("+")
        target_user = await User.objects.filter(
            phone_number__in=[target_phone, phone_without_plus],
            is_active=True,
        ).afirst()
        if not target_user:
            await message.answer(
                "❌ Bunday telefon raqam bilan foydalanuvchi topilmadi.\n\n"
                f"Telefon: <code>{target_phone}</code>"
            )
            return

        subject_id = f"user:{target_user.id}"

        if not otp_manager.can_request_otp(subject_id):
            remaining_time = otp_manager.get_remaining_time(subject_id)
            await message.answer(
                f"⏳ Juda ko'p so'rov!\n\n"
                f"Iltimos, {remaining_time} soniyadan keyin qayta urinib ko'ring."
            )
            return

        otp = otp_manager.generate_otp()
        if not otp_manager.save_otp(subject_id, otp):
            await message.answer(
                "❌ Xatolik yuz berdi!\n\n"
                "Iltimos, keyinroq qayta urinib ko'ring."
            )
            return

        await message.answer(
            "🔐 OTP tayyor.\n\n"
            f"👤 Hisob: <b>{target_user.get_full_name() or '—'}</b>\n"
            f"📱 Telefon: <code>{target_user.phone_number}</code>\n"
            f"🔑 Kod: <code>{otp}</code>\n\n"
            "⏱ Kod 5 daqiqa davomida amal qiladi."
        )
        return
    
    # User ro'yxatdan o'tganligini tekshirish
    try:
        bot_user = await BotUser.objects.aget(user_id=user_id)
        
        if not await User.objects.filter(bot_user=bot_user).aexists():
            await message.answer(
                "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
                "Avval /start buyrug'ini bosib ro'yxatdan o'ting."
            )
            return
        
    except BotUser.DoesNotExist:
        await message.answer(
            "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "Avval /start buyrug'ini bosib ro'yxatdan o'ting."
        )
        return
    
    # Rate limiting tekshirish
    if not otp_manager.can_request_otp(user_id):
        remaining_time = otp_manager.get_remaining_time(user_id)
        await message.answer(
            f"⏳ Juda ko'p so'rov!\n\n"
            f"Iltimos, {remaining_time} soniyadan keyin qayta urinib ko'ring."
        )
        return
    
    # OTP generatsiya qilish
    otp = otp_manager.generate_otp()
    
    # OTP ni Redis ga saqlash
    if not otp_manager.save_otp(user_id, otp):
        await message.answer(
            "❌ Xatolik yuz berdi!\n\n"
            "Iltimos, keyinroq qayta urinib ko'ring."
        )
        return
    
    # OTP ni yuborish
    await message.answer(
        f"🔐 Sizning login kodingiz: <code>{otp}</code>\n\n"
        f"⏱ Kod 5 daqiqa davomida amal qiladi.\n\n"
        f"💡 Bu kodni ilovangizda kiriting.\n"
        f"⚠️ Agar siz bu kodni so'ramagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring."
    )


@user_router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)


def register_routers(dp: Dispatcher):
    dp.include_router(user_router)
