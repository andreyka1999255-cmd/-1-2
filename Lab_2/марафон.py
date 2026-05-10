import logging
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

logging.basicConfig(level=logging.INFO)

TOKEN = "8737546357:AAGt0Nj_WNbM13jeJc18j3bvp44odIVZmN8"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

REGISTRATIONS_FILE = "registrations.json"

RACE_TYPES = {
    "5km":  "🏃 5 км (любительский)",
    "10km": "🏃 10 км (полупрофессиональный)",
    "21km": "🥇 21 км (полумарафон)",
    "42km": "🏆 42 км (марафон)",
}


class RegistrationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_race_type = State()


def load_registrations():
    if os.path.exists(REGISTRATIONS_FILE):
        with open(REGISTRATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_registration(user_id, username, full_name, race_type):
    registrations = load_registrations()
    registrations.append({
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "race_type": race_type,
        "race_label": RACE_TYPES[race_type],
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(REGISTRATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(registrations, f, ensure_ascii=False, indent=2)


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📝 Записаться на марафон")],
            [types.KeyboardButton(text="📋 Мои заявки")],
            [types.KeyboardButton(text="ℹ️ О марафоне")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_race_keyboard():
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=label, callback_data=f"race_{key}")]
        for key, label in RACE_TYPES.items()
    ] + [[types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]])
    return keyboard


@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🏅 Добро пожаловать в бот записи на марафон!\n\n"
        "Выбери действие в меню ниже 👇",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📝 Записаться на марафон")
async def start_registration(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationState.waiting_for_name)
    await message.answer(
        "📝 Введите ваше полное ФИО (Фамилия Имя Отчество):",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message(RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        await message.answer("❗ Введите минимум Фамилию и Имя.\nНапример: Иванов Иван Иванович")
        return
    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationState.waiting_for_race_type)
    await message.answer(
        f"✅ ФИО принято: <b>{full_name}</b>\n\n🏃 Выберите тип забега:",
        parse_mode="HTML",
        reply_markup=get_race_keyboard()
    )


@dp.callback_query(F.data.startswith("race_"), RegistrationState.waiting_for_race_type)
async def process_race_type(callback: types.CallbackQuery, state: FSMContext):
    race_key = callback.data.replace("race_", "")
    data = await state.get_data()
    full_name = data["full_name"]
    save_registration(callback.from_user.id, callback.from_user.username, full_name, race_key)
    await state.clear()
    await callback.message.edit_text(
        f"🎉 Вы успешно записаны!\n\n"
        f"👤 ФИО: <b>{full_name}</b>\n"
        f"🏃 Забег: <b>{RACE_TYPES[race_key]}</b>\n\nУдачи! 🏅",
        parse_mode="HTML"
    )
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await callback.answer()


@dp.callback_query(F.data == "cancel", RegistrationState.waiting_for_race_type)
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    await callback.answer()


@dp.message(F.text == "📋 Мои заявки")
async def my_registrations(message: types.Message):
    registrations = load_registrations()
    user_regs = [r for r in registrations if r["user_id"] == message.from_user.id]
    if not user_regs:
        await message.answer("У вас пока нет заявок.", reply_markup=get_main_keyboard())
        return
    text = "📋 <b>Ваши заявки:</b>\n\n"
    for i, reg in enumerate(user_regs, 1):
        text += f"<b>#{i}</b> {reg['full_name']} — {reg['race_label']}\n📅 {reg['registered_at']}\n\n"
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard())


@dp.message(F.text == "ℹ️ О марафоне")
async def about_marathon(message: types.Message):
    await message.answer(
        "🏅 <b>О марафоне</b>\n\n"
        "📅 Дата: 15 мая 2025 г.\n"
        "📍 Место: г. Омск, Советский парк\n"
        "🕗 Старт: 10:00\n\n"
        "Участие бесплатное! Призы победителям 🏆",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
