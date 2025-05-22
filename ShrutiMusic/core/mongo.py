from motor.motor_asyncio import AsyncIOMotorClient as mongo_client
from pymongo import MongoClient
from pyrogram import Client
import config
from ..logging import LOGGER

LOGGER(__name__).info("Connecting to MongoDB...")

if config.MONGO_DB_URI is None:
    LOGGER(__name__).error("MONGO_DB_URI not found in config!")
    exit()
else:
    mongo_async = mongo_client(config.MONGO_DB_URI)
    mongo_sync = MongoClient(config.MONGO_DB_URI)
    mongodb = mongo_async.Champu
    pymongodb = mongo_sync.Champu
    LOGGER(__name__).info("Connected to Champu Database Successfully!")
