from config.ticketsDB import client
import uuid
from utils.IST import ISTdate, ISTTime

async def createNewAdmin(admin_data:object):
    db = client["Clients"]
    collection = db[admin_data.email]

    await collection.insert_one({
        "fullname": admin_data.fullname,
        "email": admin_data.email,
        "phone": admin_data.phone,
        "password": admin_data.password,
        "key_id": str(uuid.uuid4()),
        "event_ids": [],
        "total_events": 0,
        "total_active_events": 0,
        "total_attendies": 0,
        "created_at": f"{ISTdate()} {ISTTime()}",
        "logged_out": f"{ISTdate()} {ISTTime()}",
        "is_active": False,
    })

    