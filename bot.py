# bot.py
import os
import random
import qrcode
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# -------------------------
# Настройки
# -------------------------
BOT_TOKEN = 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

IMAGES_FOLDER = os.path.join(BASE_DIR, "images")
QR_FOLDER = os.path.join(BASE_DIR, "qr")
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# -------------------------
# Состояния
# -------------------------
class RequestStates(StatesGroup):
    waiting_for_request = State()

# -------------------------
# Утилиты
# -------------------------
def generate_random_qr() -> str:
    random_string = str(random.randint(100000, 999999))
    pay_url = f"https://example.com/pay/{random_string}"
    qr_filename = f"payment_qr_{random_string}.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    img = qrcode.make(pay_url)
    img.save(qr_path)
    return qr_path

def get_random_image_path():
    valid_ext = (".jpg", ".jpeg", ".png")
    files = [f for f in os.listdir(IMAGES_FOLDER)
             if f.lower().endswith(valid_ext)]
    if not files:
        return None
    return os.path.join(IMAGES_FOLDER, random.choice(files))

# -------------------------
# Клавиатура
# -------------------------
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Каталог украшений"), KeyboardButton(text="💳 Оплата")],
        [KeyboardButton(text="🛠 Наши услуги"), KeyboardButton(text="📞 Контакты")],
        [KeyboardButton(text="⭐ Отзывы"), KeyboardButton(text="✍️ Оставить заявку")]
    ],
    resize_keyboard=True
)

# -------------------------
# Обработчики
# -------------------------
@dp.message(Command("start"))
async def start_message(message: types.Message):
    await message.answer(
        "✨ *Добро пожаловать в Ювелирную Мастерскую «Золотые Руки»!* ✨\n\n"
        "💎 Более 15 лет опыта\n"
        "💍 Индивидуальный дизайн\n"
        "🔧 Ремонт любой сложности\n\n"
        "Выберите нужный раздел 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

@dp.message(lambda m: m.text == "📸 Каталог украшений")
async def catalog(message: types.Message):
    image_path = get_random_image_path()
    if not image_path:
        await message.answer("❌ В папке `images` нет фото.")
        return

    await message.answer_photo(
        photo=FSInputFile(image_path),
        caption="💍 *Ювелирная работа на заказ*\n\n"
                "✔ Ручная работа\n"
                "✔ Гарантия качества\n"
                "✔ Индивидуальный подход\n\n"
                "📩 Хотите рассчитать стоимость? Оставьте заявку 👇",
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "💳 Оплата")
async def payment(message: types.Message):
    qr_path = generate_random_qr()
    await message.answer_photo(
        photo=FSInputFile(qr_path),
        caption="💳 *Оплата услуг*\n\n"
                "Сканируйте QR-код для оплаты.\n"
                "После оплаты напишите нам — подтвердим заказ.",
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    await message.answer(
        "📍 *Москва, ул. Тверская, 12*\n\n"
        "☎️ +7 999 222-44-55\n"
        "🕙 Пн–Пт: 10:00–19:00\n"
        "💬 Отвечаем быстро!",
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "🛠 Наши услуги")
async def services(message: types.Message):
    await message.answer(
        "🛠 *Наши услуги:*\n\n"
        "• Изготовление украшений\n"
        "• Ремонт и реставрация\n"
        "• Полировка и чистка\n"
        "• Гравировка\n"
        "• Вставка камней\n\n"
        "Консультация — бесплатно 💎",
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "⭐ Отзывы")
async def reviews(message: types.Message):
    await message.answer(
        "⭐ *Отзывы клиентов*\n\n"
        "«Качество на высшем уровне!»\n"
        "«Сделали идеальное кольцо»\n"
        "«Очень рекомендую!»",
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "✍️ Оставить заявку")
async def request_start(message: types.Message, state: FSMContext):
    await message.answer(
        "✍️ *Опишите вашу заявку*\n\n"
        "Что нужно сделать?\n"
        "Можно прикрепить фото.\n"
        "Оставьте контакт для связи.",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(RequestStates.waiting_for_request)

@dp.message(StateFilter(RequestStates.waiting_for_request))
async def request_received(message: types.Message, state: FSMContext):
    YOUR_USER_ID = 7877966673  # ✅ ТВОЙ ID

    await bot.send_message(
        YOUR_USER_ID,
        f"🔔 *Новая заявка!*\n\n"
        f"👤 {message.from_user.first_name}\n"
        f"🆔 {message.from_user.id}\n\n"
        f"{message.text}",
        parse_mode="Markdown"
    )

    await message.answer(
        "✅ Заявка принята!\nМы свяжемся с вами в ближайшее время 💎",
        reply_markup=main_keyboard
    )
    await state.clear()

# -------------------------
# Запуск
# -------------------------
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
