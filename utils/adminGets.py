from config.ticketsDB import client
from bson.objectid import ObjectId

async def checkAdmin(email:str):
    db = client["Clients"]
    collection = await db.list_collection_names()

    if email in collection:
        return True
    else:
        return False
    
async def checkAdminPassword(email:str, password:str):
    db = client["Clients"]
    collection = db[email]
    data = await collection.find_one({"password": password})
    if data:
        return True
    else:
        return False

async def getAdminDashboardData(email:str):
    db = client["Clients"]
    db2 = client["Events"]

    collection = db[email]
    admin_data = await collection.find({}, {"_id": 0}).to_list(None)
    recent_event = []
    admin_data_dict ={
        "total_events": admin_data[0]["total_events"],
        "total_active_events": admin_data[0]["total_active_events"],
        "total_attendies": admin_data[0]["total_attendies"],
        "recent_events": recent_event
    }
    if admin_data[0]["total_events"] > 0:
        event_collection = db2[email]
        event_data = (await event_collection.find({}, {"_id": 0}).to_list(None))[::-1][0:3]
        total_events = len(event_data)
        for event in range(0, total_events):
            evnt_date = f"{event_data[event]['start_date']} - {event_data[event]['end_date']}"
            recent_event_info = [event_data[event]["event_name"], evnt_date, event_data[event]["total_attendies"]]
            recent_event.append(recent_event_info)
    else:
        recent_event = []
                
    return admin_data_dict

        
async def getAdminSecurityData(email:str):
    db = client["Clients"]
    collection = db[email]
    security_data = await collection.find({}, {"_id": 0}).to_list(None)
    security_data_dict = {
        "key_id":security_data[0]["key_id"],
        "event_tokens":security_data[0]["event_ids"]
    }
    return security_data_dict

async def getAdminEvents(email:str):
    db = client["Events"]
    collection = db[email]
    event_data = (await collection.find({}).to_list(None))[::-1]
    event_data_list = []
    event_data_dict = {}
    for event in event_data:
        event_one_data = {}
        event_one_data["event_name"] = event["event_name"]
        event_date = f"{event['start_date']} - {event['end_date']}"
        event_one_data["event_date"] = event_date
        event_one_data["total_tickets_sold"] = event["total_generated_tickets"]
        event_one_data["status"] = event["is_active"]

        event_id = str(event["_id"])

        event_data_dict[event_id] = event_one_data
        event_data_list.append(event_data_dict)
        event_data_dict = {}


    return event_data_list


async def getEventAttendees(email:str, event_id:str):
    db = client["Events"]
    db2 = client["Tickets"]
    collection = db[email]
    object_id = ObjectId(event_id)

    result = await collection.find_one(
        {"_id": object_id},
        {"event_token": 1, "total_generated_tickets": 1, "_id": 0}
    )

    event_token = result.get("event_token")
    total_generated_tickets = result.get("total_generated_tickets")

    if total_generated_tickets > 0:
        collections = await db2.list_collection_names()
        if event_token in collections:
            collection = db2[event_token]
            attendees = await collection.find({}, {"_id": 0, "signature": 0}).to_list(None)
            return attendees
        else:
            return []
    else:
        return []

    