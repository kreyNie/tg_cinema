import os
import logging
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=os.getenv("TGToken"))

ADMIN_IDS = (None,)
