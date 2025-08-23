import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart

bot = Bot("6383859349:AAGHk44MuOTWV3_qWwGsq-ciAOC1RByuaog")
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(m: types.Message):
    await m.answer("Привет! Я на aiogram v3.")

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
