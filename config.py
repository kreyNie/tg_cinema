import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG", 0)
bot = Bot(token=os.getenv("TGToken"))

ADMIN_IDS = (None,)
