from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import redis.asyncio as redis
import os
import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = '7013260741:AAHwjBU7kPuvx0-P9AuUBmLXczuTDeBJm6k'
REDIS_HOST = 'redis'
REDIS_PORT = 6379

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


async def get_currency_rate(code):
    if code.upper() == 'RUB':
        return 1.0
    return await redis_client.get(code.upper())


@dp.message(Command('exchange'))
async def exchange(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            await message.reply("Неверный формат команды. Используйте /exchange ИЗ_ВАЛЮТЫ В_ВАЛЮТУ КОЛИЧЕСТВО_ВАЛЮТЫ")
            return

        _, from_currency, to_currency, amount = parts
        amount = float(amount)

        from_rate = await get_currency_rate(from_currency)
        to_rate = await get_currency_rate(to_currency)

        if from_rate is None:
            await message.reply(f"Неверный код валюты: {from_currency}")
            return

        if to_rate is None:
            await message.reply(f"Неверный код валюты: {to_currency}")
            return

        if from_currency.upper() == 'RUB':
            result = amount / float(to_rate)
            await message.reply(f"{amount} RUB = {result:.2f} {to_currency}")
        elif to_currency.upper() == 'RUB':
            result = amount * float(from_rate)
            await message.reply(f"{amount} {from_currency} = {result:.2f} RUB")
        else:
            result = amount * float(from_rate) / float(to_rate)
            await message.reply(f"{amount} {from_currency} = {result:.2f} {to_currency}")
    except Exception as e:
        logging.error(f"Ошибка обработки команды обмена валюты: {e}")
        await message.reply("Ошибка при обработке вашего запроса.")


@dp.message(Command('rates'))
async def rates(message: types.Message):
    try:
        currencies = await redis_client.keys('*')
        rates = {currency: await redis_client.get(currency) for currency in currencies}
        rates_message = "\n".join([f"{code}: {rate}" for code, rate in rates.items()])
        await message.reply(f"Текущий курс валют (в RUB):\n{rates_message}")
    except Exception as e:
        logging.error(f"Ошибка обработки команды получения курса валют: {e}")
        await message.reply("Ошибка при получении курса валют.")


async def on_startup(dispatcher: Dispatcher):
    logging.info("Starting bot...")


async def on_shutdown(dispatcher: Dispatcher):
    logging.info("Shutting down...")


if __name__ == '__main__':
    from aiogram import Dispatcher
    from aiogram import Bot
    from aiogram import types


    async def main():
        await on_startup(dp)
        try:
            await dp.start_polling(bot)
        finally:
            await on_shutdown(dp)


    import asyncio

    asyncio.run(main())
