"""
Telegram-бот "Сайты-помощник"
- /start — меню категорий (inline-кнопки)
- выбор категории — список сайтов с описанием
- текстовый запрос — поиск по названию/описанию/тегам
- /help — справка

Установка:
    pip install aiogram==3.* python-dotenv
    export BOT_TOKEN="токен_от_BotFather"
Запуск:
    python bot.py
"""

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬТЕ_ТОКЕН")

# ---------------------------------------------------------------------------
# КАТАЛОГ. Меняйте под свою задачу: ключ — код категории.
# Формат записи: (название, ссылка, короткое описание, теги)
# ---------------------------------------------------------------------------
CATALOG: dict[str, dict] = {
    "work": {
        "title": "💼 Работа и фриланс",
        "url": "https://hh.ru",
        "desc": "Поиск вакансий и резюме",
        "tags": ["работа", "вакансии", "hh"],
    },
    "study": {
        "title": "📚 Обучение",
        "url": "https://stepik.org",
        "desc": "Курсы по программированию и не только",
        "tags": ["курсы", "учёба", "обучение", "stepik"],
    },
    "design": {
        "title": "🎨 Дизайн и графика",
        "url": "https://www.figma.com",
        "desc": "Онлайн-редактор интерфейсов",
        "tags": ["дизайн", "figma", "макет"],
    },
    "ai": {
        "title": "🤖 ИИ-сервисы",
        "url": "https://mashagpt.ru",
        "desc": "Чат, генерация картинок, видео, музыка",
        "tags": ["ии", "ai", "gpt", "нейросети"],
    },
    "docs": {
        "title": "📄 Документы и PDF",
        "url": "https://www.ilovepdf.com",
        "desc": "Объединить, сжать, конвертировать PDF",
        "tags": ["pdf", "документы", "конвертер"],
    },
}

# Быстрое наполнение: чуть расширенный каталог по категориям
CATEGORIES: dict[str, list[str]] = {
    "Работа и фриланс": ["work"],
    "Обучение": ["study"],
    "Дизайн и графика": ["design"],
    "ИИ-сервисы": ["ai"],
    "Документы и PDF": ["docs"],
}

dp = Dispatcher()


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat, keys in CATEGORIES.items():
        kb.button(text=cat, callback_data=f"cat:{cat}")
    kb.button(text="🎲 Случайный сайт", callback_data="random")
    kb.adjust(2)
    return kb.as_markup()


def items_of(cat: str) -> list[str]:
    return CATEGORIES.get(cat, [])


def render(code: str) -> str:
    item = CATALOG[code]
    return f"<b>{item['title']}</b>\n{item['desc']}\n🔗 {item['url']}"


def search(query: str) -> list[str]:
    q = query.strip().lower()
    if not q:
        return []
    found = []
    for code, item in CATALOG.items():
        haystack = " ".join(
            [item["title"], item["desc"], *item["tags"]]
        ).lower()
        if q in haystack:
            found.append(code)
    return found


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я помогу найти нужные сайты.\n\n"
        "Выберите категорию кнопкой ниже или просто напишите, что ищете "
        "(например: <i>курсы</i>, <i>pdf</i>, <i>нейросети</i>).",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Как пользоваться:\n"
        "• /start — меню категорий\n"
        "• напишите слово — я поищу по каталогу\n"
        "• кнопка «Случайный сайт» — сюрприз 🙂"
    )


@dp.callback_query(F.data == "random")
async def cb_random(call: CallbackQuery) -> None:
    import random

    code = random.choice(list(CATALOG))
    await call.message.answer(render(code))
    await call.answer()


@dp.callback_query(F.data.startswith("cat:"))
async def cb_category(call: CallbackQuery) -> None:
    cat = call.data.split(":", 1)[1]
    codes = items_of(cat)
    if not codes:
        await call.answer("Пусто", show_alert=True)
        return

    text = "\n\n".join(render(c) for c in codes)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")]
        ]
    )
    await call.message.answer(text, reply_markup=kb, disable_web_page_preview=True)
    await call.answer()


@dp.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery) -> None:
    await call.message.answer("Выберите категорию:", reply_markup=main_menu())
    await call.answer()


@dp.message(F.text)
async def on_text(message: Message) -> None:
    results = search(message.text)
    if not results:
        await message.answer(
            "Ничего не нашла 😔 Попробуйте другое слово "
            "или выберите категорию:",
            reply_markup=main_menu(),
        )
        return

    for code in results:
        await message.answer(render(code), disable_web_page_preview=True)

    if len(results) > 1:
        await message.answer("Может, ещё что-то?", reply_markup=main_menu())


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    print("Бот запущен. Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
