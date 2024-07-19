import aiohttp
import xml.etree.ElementTree as ET
import redis
import asyncio
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
XML_URL = os.getenv('XML_URL')

logging.basicConfig(level=logging.INFO)


async def fetch_xml():
    async with aiohttp.ClientSession() as session:
        async with session.get(XML_URL) as response:
            return await response.text()


def parse_xml(xml_data):
    root = ET.fromstring(xml_data)
    currencies = {}
    for child in root.findall('Valute'):
        char_code = child.find('CharCode').text
        value = float(child.find('Value').text.replace(',', '.'))
        nominal = int(child.find('Nominal').text)
        currencies[char_code] = value / nominal
    return currencies


async def update_redis():
    xml_data = await fetch_xml()
    currencies = parse_xml(xml_data)
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    for code, rate in currencies.items():
        r.set(code, rate)
    logging.info("Currency rates updated in Redis")


async def scheduled_task():
    while True:
        now = datetime.now()
        next_run = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        wait_time = (next_run - now).total_seconds()
        logging.info(f"Next update scheduled in {wait_time} seconds")
        await asyncio.sleep(wait_time)
        await update_redis()


async def main():
    await update_redis()
    await scheduled_task()


if __name__ == "__main__":
    asyncio.run(main())
