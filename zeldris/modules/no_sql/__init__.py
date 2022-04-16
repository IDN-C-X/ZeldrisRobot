#  ZeldrisRobot
#  Copyright (C) 2017-2019, Paul Larsen
#  Copyright (C) 2022, IDNCoderX Team, <https://github.com/IDN-C-X/ZeldrisRobot>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

"""MongoDB Database."""

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from pymongo import MongoClient, collection

from zeldris import MONGO_DB, MONGO_PORT, MONGO_URI

# MongoDB Client
mongodb = MongoClient(MONGO_URI, MONGO_PORT)[MONGO_DB]
motor = AsyncIOMotorClient(MONGO_URI)
db = motor[MONGO_DB]
engine = AIOEngine(motor, MONGO_DB)
DB_CLIENT = MongoClient(MONGO_URI)
_DB = DB_CLIENT["Zeldris"]


def get_collection(name: str) -> collection:
    """Get the collection from database."""
    return _DB[name]
