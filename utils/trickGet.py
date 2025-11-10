from config.ticketsDB import client
from utils.IST import ISTdate, ISTTime
from bson.objectid import ObjectId
from utils.adminPuts import updateEventAttendeesCount
from utils.adminGets import checkTokenExpiry

# async def verify_ticket_admin(ticket:str, token:str):
#     db = client["Tickets"]
#     db2 = client["TicVer"]
#     collection2 = db2["ticMaps"]
#     collection2_data = await collection2.find({}, {"_id": 0}).to_list(None)
#     id_mappingg = collection2_data[0]["id_mapping"]
#     ticket_ids = id_mappingg[token]
#     print(token)
#     print(mappingg)
#     if ticket in ticket_ids:
#         ticket_id = mappingg[token]
#         tokens = await db.list_collection_names()
#         if token in tokens:
#             collection = db[token]
#             ticket_data = await collection.find_one({"_id": ObjectId(ticket_id)})
#             if not ticket_data["attended"] :
#                 time = f"{ISTdate()} {ISTTime()}"
#                 await collection.update_one(
#                     {"_id": ObjectId(ticket_id)},
#                     {"$set":{"attended":True, "attending_time":time}}
#                 )
#                 return True
#             else:
#                 return False
#         else:
#             return False
#     else:
#         return False

async def verify_ticket_admin(ticket:str, token:str):
    db = client["Tickets"]
    collection = db[token]
    ticket_data = await collection.find_one({"ticket_id": ticket})
    is_expired = await checkTokenExpiry(token=token)
    if not is_expired:
        if ticket_data:
            if not ticket_data["attended"] :
                time = f"{ISTdate()} {ISTTime()}"
                await collection.update_one(
                    {"ticket_id": ticket},
                    {"$set":{"attended":True, "attending_time":time}}
                )
                await updateEventAttendeesCount(token)
                return True
            else:
                return False
        else:
            return False
    return False


async def get_ticket_info(ticket:str):

    ticket_collection, email_acc = await get_ticket_collection(ticket_id=ticket)
    if ticket_collection:
        db = client["Tickets"]
        tickets = await db.list_collection_names()
        if ticket_collection in tickets:
            collection = db[ticket_collection] #here ticket_collection is event_token
            is_expired = await checkTokenExpiry(token= ticket_collection)
            ticket_data = await collection.find_one({"ticket_id": ticket})
            if not ticket_data["attended"]:
                if is_expired:
                    valid = False
                else:
                    valid = True
            else:
                valid = False

            name = ticket_data["name"]
            email = ticket_data["email"]
            phone = ticket_data["phone"]

            db2 = client["Events"]
            collection2 = db2[email_acc]

            event_data = await collection2.find_one({"event_token":ticket_collection})

            tic_details = {
                "name" : name,
                "email" : email,
                "phone" : phone,
                "valid" : valid,
                "expiry" : event_data["expiry"],
                "event_name":event_data["event_name"],
                "eve_location":event_data["event_location"],
                "event_start":event_data["start_date"]
            }
            return tic_details
            
        else:
            return False
    else:
        return False
    

async def just_check_ticket(ticket:str):
    ticket_collection, email = await get_ticket_collection(ticket_id=ticket)
    if ticket_collection:
        return True
    else:
        return False


async def get_ticket_collection(ticket_id:str):
    db = client["TicVer"]
    collection = db["ticMaps"]
    data = await collection.find({}, {"_id": 0}).to_list(None)
    id_mapping = data[0]["id_mapping"]
    if id_mapping:
        for key, value in id_mapping.items():
            if ticket_id in value:
                db2 = client["Redirects"]
                collection2 = db2["secrets"]

                secret_data = (await collection2.find({}, {"_id":0}).to_list(None))[0]["tokens"]
                for secret in secret_data:
                    if secret[0] == key:
                        return key, secret[1] # secret[1] is email
        return False
    else:
        return False
 