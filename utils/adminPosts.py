from config.ticketsDB import client
import uuid
from utils.IST import ISTdate, ISTTime
from utils.adminPuts import updateEventsStatus
from utils.adminPuts import updateRedirect, updateRedirectKeys

async def createNewAdmin(admin_data:object):
    db = client["Clients"]
    collection = db[admin_data.email]
    key_id = str(uuid.uuid4())
    await collection.insert_one({
        "fullname": admin_data.fullname,
        "email": admin_data.email,
        "phone": admin_data.phone,
        "password": admin_data.password,
        "key_id": key_id,
        "event_ids": [],
        "total_events": 0,
        "total_active_events": 0,
        "total_attendies": 0,
        "created_at": f"{ISTdate()} {ISTTime()}",
        "logged_out": f"{ISTdate()} {ISTTime()}",
        "is_active": False,
    })

    await updateRedirectKeys(key = key_id)

async def hostEvent(hosting:object, email:str):
    db = client["Events"]
    collection = db[email]
    if hosting.expiry == "":
        hosting.expiry = hosting.end_date
        
    result = await collection.insert_one({
        "event_name": hosting.event_name,
        "company_name": hosting.company_name,
        "event_location": hosting.event_location,
        "start_date": hosting.start_date,
        "end_date": hosting.end_date,
        "ticket_cost": int(hosting.ticket_cost),
        "expiry": hosting.expiry,
        "ticket_limit": int(hosting.ticket_limit),
        "event_token": hosting.event_token,
        "total_attendies": 0,
        "total_generated_tickets": 0,
        "created_at": f"{ISTdate()} {ISTTime()}",
        "logged_out": "",
        "is_active": True,
    })
    event_infos = [str(result.inserted_id), (hosting.event_name).title(), hosting.event_token]
    await updateEventsStatus(email, event_infos)
    await updateRedirect(hosting.event_token, email)
    return True