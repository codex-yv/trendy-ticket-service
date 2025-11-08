from config.ticketsDB import client

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
        recent_events_id = admin_data[0]["event_ids"][::-1][0:3]
        for event_id in recent_events_id:
            event_collection = db2[event_id]
            event_data = await event_collection.find({}, {"_id": 0}).to_list(None)
            evnt_date = f"{event_data[0]['start_date']} - {event_data[0]['end_date']}"
            recent_event_info = [event_data[0]["event_name"], evnt_date, event_data[0]["total_attendies"]]
            recent_event.append(recent_event_info)
    else:
        recent_event = []
                
    return admin_data_dict

        

