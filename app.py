import asyncio
import logging
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = "8753641231:AAHBC4LVOlTtp1xhQ9d4prRP_hkSGnoN1Rs"
ADMIN_ID = 217924651
SERVICE_ID = "219701"
RENEWAL_URL = "https://dash.hidencloud.com/clientarea.php?action=productdetails&id=219701"
REMIND_EVERY_DAYS = 6

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def renewal_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть дашборд", url=RENEWAL_URL)],
        [InlineKeyboardButton(text="Продлил", callback_data="renewed")],
        [InlineKeyboardButton(text="Напомни через 12ч", callback_data="snooze")],
    ])

async def send_reminder():
    await bot.send_message(ADMIN_ID, "HidenCloud - пора продлить сервер! Истекает завтра.", parse_mode="HTML", reply_markup=renewal_kb())

@dp.message(Command("start"))
async def start(msg: Message):
    if msg.from_user.id != ADMIN_ID: return
    await msg.answer("Renewal Bot запущен! /status - статус", parse_mode="HTML")

@dp.message(Command("status"))
async def status(msg: Message):
    if msg.from_user.id != ADMIN_ID: return
    jobs = scheduler.get_jobs()
    next_run = next((j.next_run_time for j in jobs if j.id == "reminder"), None)
    next_str = next_run.strftime("%d.%m.%Y %H:%M") if next_run else "нет"
    await msg.answer(f"Следующее напоминание: {next_str}", parse_mode="HTML")

@dp.message(Command("remind"))
async def remind(msg: Message):
    if msg.from_user.id != ADMIN_ID: return
    await send_reminder()

@dp.callback_query(F.data == "renewed")
async def cb_renewed(call: CallbackQuery):
    await call.message.edit_text("Отлично! Сервер продлён.")
    await call.answer()

@dp.callback_query(F.data == "snooze")
async def cb_snooze(call: CallbackQuery):
    t = datetime.now() + timedelta(hours=12)
    scheduler.add_job(send_reminder, trigger="date", run_date=t, id="snooze", replace_existing=True)
    await call.message.edit_text(f"Напомню в {t.strftime('%H:%M')}")
    await call.answer()

async def main():
    scheduler.add_job(send_reminder, trigger="interval", days=REMIND_EVERY_DAYS, id="reminder")
    scheduler.start()
    await bot.send_message(ADMIN_ID, "Bot started!")
    await dp.start_polling(bot)

asyncio.run(main())
