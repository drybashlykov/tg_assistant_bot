# demo_aiogram3_bot.py
# Полноценная демка aiogram v3 в одном файле.

import os
import asyncio
import logging
from datetime import datetime, timedelta
from random import randint

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import CommandStart, Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ---------- базовая настройка ----------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN") or "PUT_YOUR_TOKEN_HERE"
if BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
    raise SystemExit("Установите переменную окружения BOT_TOKEN с токеном вашего бота.")

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# список «админов» для примера (замените на свои ID)
ADMIN_IDS = {123456789}

# ---------- клавиатуры ----------
def kb_reply_main() -> types.ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text="⏰ Время")
    b.button(text="🎲 Рандом")
    b.button(text="📋 Форма")
    b.button(text="🧹 Убрать клавиатуру")
    b.adjust(2, 2)
    return b.as_markup(resize_keyboard=True)

def kb_inline_menu(counter: int = 0) -> types.InlineKeyboardMarkup:
    ib = InlineKeyboardBuilder()
    ib.button(text=f"➕ Счётчик: {counter}", callback_data=f"cnt:{counter}")
    ib.button(text="🕒 Время", callback_data="time")
    ib.button(text="🎯 Случайно 1–100", callback_data="rand")
    ib.adjust(1, 2)
    return ib.as_markup()

# ---------- машина состояний (FSM) ----------
class Form(StatesGroup):
    name = State()
    age = State()
    mood = State()

# ---------- команды ----------
@router.message(CommandStart())
async def cmd_start(m: types.Message):
    await m.answer(
        f"Привет, <b>{m.from_user.full_name}</b>!\n"
        "Это демо aiogram v3: команды, FSM, клавиатуры, callback, inline-mode и т.д.\n"
        "Наберите /help, чтобы увидеть список.",
        reply_markup=kb_reply_main()
    )

@router.message(Command("help"))
async def cmd_help(m: types.Message):
    await m.answer(
        "Доступно:\n"
        "/help — справка\n"
        "/menu — инлайн-меню (callback)\n"
        "/form — демо формы (FSM)\n"
        "/cancel — отменить форму\n"
        "/dice — бросить кости/дартс и т.п.\n"
        "/remindme <сек> <текст> — напоминание через N секунд\n"
        "/me — инфо о вас/чате\n"
        "/kb — показать / скрыть реплай-клавиатуру\n"
        "/long — имитация долгой операции с «печатает…»\n"
        "/pin — закрепить сообщение (для ADMIN_IDS)\n"
        "Также: пришлите фото/документ/голос — бот ответит."
    )

@router.message(Command("menu"))
async def cmd_menu(m: types.Message):
    await m.answer("Инлайн-меню (callback-кнопки) ниже:", reply_markup=kb_inline_menu())

@router.message(Command("kb"))
async def cmd_kb(m: types.Message):
    if m.text.strip() == "/kb":
        # Тоггл клавиатуры: если уже есть — уберём, иначе покажем
        await m.answer("Показываю клавиатуру.", reply_markup=kb_reply_main())
    else:
        await m.answer("Убираю клавиатуру.", reply_markup=types.ReplyKeyboardRemove())

@router.message(Command("me"))
async def cmd_me(m: types.Message):
    u = m.from_user
    chat = m.chat
    await m.answer(
        "👤 <b>Пользователь</b>\n"
        f"ID: <code>{u.id}</code>\n"
        f"Username: @{u.username}\n"
        f"Имя: {u.full_name}\n\n"
        "💬 <b>Чат</b>\n"
        f"ID: <code>{chat.id}</code>\n"
        f"Тип: {chat.type}"
    )

@router.message(Command("dice"))
async def cmd_dice(m: types.Message):
    # Несколько бросков с разными эмодзи
    for emoji in ("🎲", "🎯", "🏀", "🎳", "⚽", "🎰"):
        await m.answer_dice(emoji=emoji)
        await asyncio.sleep(0.5)

@router.message(Command("long"))
async def cmd_long(m: types.Message):
    # Показ «печатает…» во время долгой операции
    async with ChatActionSender.typing(bot=bot, chat_id=m.chat.id):
        await asyncio.sleep(2.5)
    await m.answer("Готово! Это была долгая имитационная операция.")

@router.message(Command("pin"))
async def cmd_pin(m: types.Message):
    if m.from_user.id not in ADMIN_IDS:
        return await m.answer("Команда доступна только администраторам демо (см. ADMIN_IDS).")
    try:
        await bot.pin_chat_message(chat_id=m.chat.id, message_id=m.message_id)
        await m.answer("Сообщение закреплено.")
    except Exception as e:
        await m.answer(f"Не удалось закрепить: <code>{e}</code>")

# ---------- callback-кнопки ----------
@router.callback_query(F.data == "time")
async def cb_time(q: types.CallbackQuery):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await q.answer(f"Сейчас: {now}", show_alert=False)

@router.callback_query(F.data == "rand")
async def cb_rand(q: types.CallbackQuery):
    await q.answer(f"Случайное число: {randint(1, 100)}")

@router.callback_query(F.data.startswith("cnt:"))
async def cb_counter(q: types.CallbackQuery):
    try:
        _, raw = q.data.split(":", 1)
        value = int(raw) + 1
    except Exception:
        value = 1
    # Обновим текст и клавиатуру
    if q.message:
        await q.message.edit_reply_markup(reply_markup=kb_inline_menu(value))
    await q.answer("++")

# ---------- FSM: простая «анкета» ----------
@router.message(Command("form"))
async def form_start(m: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await m.answer("Как вас зовут? (или /cancel)")

@router.message(Command("cancel"))
async def form_cancel(m: types.Message, state: FSMContext):
    if await state.get_state() is None:
        return await m.answer("Отменять нечего.")
    await state.clear()
    await m.answer("Форма отменена.", reply_markup=kb_reply_main())

@router.message(Form.name, F.text)
async def form_name(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await state.set_state(Form.age)
    await m.answer("Сколько вам лет? (числом)")

@router.message(Form.age, F.text)
async def form_age(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer("Возраст должен быть числом, попробуйте ещё раз.")
    await state.update_data(age=int(m.text))
    await state.set_state(Form.mood)
    await m.answer("Как настроение? (коротко)")

@router.message(Form.mood, F.text)
async def form_done(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await m.answer(
        "Готово! Данные формы:\n"
        f"Имя: <b>{data.get('name')}</b>\n"
        f"Возраст: <b>{data.get('age')}</b>\n"
        f"Настроение: <b>{m.text.strip()}</b>"
    )

# ---------- напоминание с таймером ----------
@router.message(Command("remindme"))
async def cmd_remindme(m: types.Message):
    # формат: /remindme <секунды> <текст...>
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await m.answer("Формат: /remindme <секунды> <текст>\nНапр.: /remindme 10 выпить воду")
    delay = int(parts[1])
    text = parts[2].strip()
    when = datetime.now() + timedelta(seconds=delay)
    await m.answer(f"Ок! Напомню в {when:%H:%M:%S}: “{text}”")

    async def _task():
        await asyncio.sleep(delay)
        try:
            await bot.send_message(m.chat.id, f"🔔 Напоминание: {text}")
        except Exception as e:
            logging.exception("Не удалось отправить напоминание: %r", e)

    asyncio.create_task(_task())

# ---------- обработка разных типов контента ----------
@router.message(F.photo)
async def got_photo(m: types.Message):
    p = m.photo[-1]  # максимальное качество
    await m.answer_photo(p.file_id, caption=f"Фото получено! file_id: <code>{p.file_id}</code>")

@router.message(F.document)
async def got_document(m: types.Message):
    d = m.document
    await m.answer(
        "Документ получен:\n"
        f"Имя: <code>{d.file_name}</code>\nРазмер: <code>{d.file_size}</code>\nMIME: <code>{d.mime_type}</code>"
    )

@router.message(F.voice)
async def got_voice(m: types.Message):
    await m.answer_voice(m.voice.file_id, caption="Голосовое эхо!")

# ---------- обработка «реплай-клавиатуры» по тексту ----------
@router.message(Text("⏰ Время"))
async def btn_time(m: types.Message):
    await m.answer(datetime.now().strftime("Сейчас %Y-%m-%d %H:%M:%S"))

@router.message(Text("🎲 Рандом"))
async def btn_rand(m: types.Message):
    await m.answer(str(randint(1, 100)))

@router.message(Text("📋 Форма"))
async def btn_form(m: types.Message, state: FSMContext):
    await form_start(m, state)

@router.message(Text("🧹 Убрать клавиатуру"))
async def btn_hide_kb(m: types.Message):
    await m.answer("Спрятал клавиатуру.", reply_markup=types.ReplyKeyboardRemove())

# ---------- inline-mode (включите в BotFather) ----------
@router.inline_query()
async def inline_echo(q: types.InlineQuery):
    # простая выдача: отдать обратно то, что запросили
    text = q.query or "Пустой запрос"
    results = [
        types.InlineQueryResultArticle(
            id="echo",
            title="Эхо",
            input_message_content=types.InputTextMessageContent(f"📣 {text}")
        ),
        types.InlineQueryResultArticle(
            id="time",
            title="Текущее время",
            input_message_content=types.InputTextMessageContent(
                datetime.now().strftime("Сейчас %Y-%m-%d %H:%M:%S")
            )
        ),
    ]
    await q.answer(results=results, cache_time=1, is_personal=True)

# ---------- эхо-обработчик (последний) ----------
@router.message(F.chat.type == "private", F.text)
async def echo_private(m: types.Message):
    if m.text.startswith("/"):
        # неизвестная команда — краткий ответ
        return await m.answer("Не знаю такой команды. Попробуйте /help.")
    await m.answer(f"Эхо: <code>{m.text}</code>")

@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def echo_group(m: types.Message):
    await m.reply("Я услышал: " + m.text)

# ---------- запуск ----------
async def main():
    logging.info("Бот запускается…")
    await dp.start_polling(bot, allowed_updates=types.ALL_UPDATE_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
