from config.ticketsDB import client
import uuid
from bson.objectid import ObjectId

async def updateAdminKey(email:str):
    db = client["Clients"]
    collection = db[email]
    new_key = str(uuid.uuid4())
    await collection.update_one(
        {"email":email},
        {"$set": {"key_id": new_key}}
    )
    
    return new_key

async def updateEventsStatus(email:str, event_info:list):
    db = client["Clients"]
    collection = db[email]
    
    current_data = await collection.find({}, {"_id": 0}).to_list(None)
    new_event = current_data[0]["event_ids"]
    new_event.append(event_info)

    total_events = current_data[0]["total_events"]
    total_events += 1
    
    await collection.update_one(
        {"email":email},
        {"$set": {"event_ids": new_event, "total_events": total_events}}
    )

async def deteleEvent(email:str, event_id:str):
    db = client["Events"]
    collection = db[email]
    await collection.delete_one({"_id": ObjectId(event_id)})

    db2 = client["Clients"]
    collection2 = db2[email]

    current_data = await collection2.find({}, {"_id": 0}).to_list(None)
    old_event = current_data[0]["event_ids"]
    new_events = []
    for event in old_event:
        if event[0] != event_id:
            new_events.append(event)

    total_events = current_data[0]["total_events"]
    total_events -= 1

    await collection2.update_one(
        {"email":email},
        {"$set": {"event_ids": new_events, "total_events": total_events}}
    )
    