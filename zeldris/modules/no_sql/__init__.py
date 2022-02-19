"""MongoDB Database."""

from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pymongo import MongoClient, collection

from zeldris import MONGO_DB, MONGO_PORT, MONGO_URI

# MongoDB Client
mongodb = MongoClient(MONGO_URI, 27017)[MONGO_DB]
motor = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = motor[MONGO_DB]
engine = AIOEngine(motor, MONGO_DB)
DB_CLIENT = MongoClient(MONGO_URI)
_DB = DB_CLIENT["Zeldris"]


def get_collection(name: str) -> collection:
    """Get the collection from database."""
    return _DB[name]
