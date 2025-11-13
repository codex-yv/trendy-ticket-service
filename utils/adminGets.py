import collections
from config.ticketsDB import client
from bson.objectid import ObjectId
from utils.general import is_expiry_exceeded
from utils.IST import ISTdate, ISTTime
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
        event_one_data["revenue"] = await getEventRevenue(token=event["event_token"])
        event_id = str(event["_id"])

        event_data_dict[event_id] = event_one_data
        event_data_list.append(event_data_dict)
        event_data_dict = {}

    print(event_data_list)

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
            collection2 = db2[event_token]
            attendees = await collection2.find({}, {"_id": 0, "signature": 0}).to_list(None)
            return attendees
        else:
            return []
    else:
        return []


async def checkRedirectTTS(key:str, token:str):
    db = client["Redirects"]
    collection = db["secrets"]

    data = await collection.find({}, {"_id": 0}).to_list(None)
    # print(data)
    if data:
        if key in data[0]["keys"]:
            for tokenn in data[0]["tokens"]:
                if tokenn[0] == token:
                    return True
            return False
        else:
            return False
    else:
        return False


async def verifyAdminforScan(token:str, key:str):
    db = client["Redirects"]
    collection = db["secrets"]
    db2 = client["Events"]
    data = await collection.find({}, {"_id": 0}).to_list(None)
    if data:
        if key in data[0]["keys"]:
            for tokenn in data[0]["tokens"]:
                if tokenn[0] == token:
                    is_expired = await checkTokenExpiry(token=token)
                    
                    if is_expired:
                        return -1
                    else:
                        return True
            return -1
        else:
            return 0
    else:
        return 0


async def checkTokenExpiry(token:str):
    db = client["Redirects"]
    collection = db["secrets"]

    data = await collection.find({}, {"_id": 0}).to_list(None)
    for tokenn in data[0]["tokens"]:
        if tokenn[0] == token:
            db2 = client["Events"]
            collection2 = db2[tokenn[1]]
            event_data = await collection2.find_one({"event_token":token})
            expiry = event_data["expiry"]
            is_active = event_data["is_active"]
            if is_active:
                is_expired = await is_expiry_exceeded(date=ISTdate(), time=ISTTime(), exp_date=expiry)
                if is_expired:
                    await collection2.update_one(
                        {"event_token":token},
                        {"$set":{"is_active":False}}
                    )
                    db3 = client["Clients"]
                    collection3 = db3[tokenn[1]]
                    await collection3.update_one(
                        {"email":tokenn[1]},
                        {"$inc":{"total_active_events":-1}}
                    )
                    return True
                else:
                    return False
            else:
                return True
        
async def getEventRevenue(token:str):
    db = client["Tickets"]
    collection = db[token]

    event_data = await collection.find({}, {"_id":0}).to_list(None)

    revenue = 0
    for event in event_data:
        amount = event["amount"]
        revenue+=amount
    
    return revenue