from hmac import new
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
    
    total_active_events = current_data[0]["total_active_events"]
    total_active_events += 1
    
    await collection.update_one(
        {"email":email},
        {"$set": {"event_ids": new_event, "total_events": total_events, "total_active_events": total_active_events}}
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
    event_token = ""
    for event in old_event:
        if event[0] != event_id:
            new_events.append(event)
        else:
            event_token = event[2]

    total_active_events = current_data[0]["total_active_events"]
    total_active_events -= 1
    
    await collection2.update_one(
        {"email":email},
        {"$set": {"event_ids": new_events, "total_active_events": total_active_events}}
    )
    db3 = client["Redirects"]
    collection3 = db3["secrets"]
    tokens = (await collection3.find({}, {"_id": 0}).to_list(None))[0]["tokens"]
    new_token = []
    for token in tokens:
        if token[0] != event_token:
            new_token.append(token)
        
    
    await collection3.update_one(
        {"_id":ObjectId("690f8c2a5d7cf53e815adf0d")},
        {"$set": {"tokens": new_token}}
    )

    db4 = client["TicVer"]
    collection4 = db4["ticMaps"]
    c4_result = await collection4.find({}, {"_id": 0}).to_list(None)
    mapping = c4_result[0]["mapping"]
    id_mapping = c4_result[0]["id_mapping"]
    
    if event_token in mapping:
        del mapping[event_token]
    if event_token in id_mapping:
        del id_mapping[event_token]
    
    await collection4.update_one(
        {"_id":ObjectId("6910e37a2b3d2191a187a5d6")},
        {"$set": {"mapping": mapping, "id_mapping": id_mapping}}
    )
    
    
async def updateRedirect(token:str, email:str):
    db = client["Redirects"]
    collection = db["secrets"]
    tokens = (await collection.find({}, {"_id": 0}).to_list(None))[0]["tokens"]
    new_tokens = [token, email]
    tokens.append(new_tokens)
    await collection.update_one(
        {"_id":ObjectId("690f8c2a5d7cf53e815adf0d")},
        {"$set": {"tokens": tokens}}
    )

async def updateTicketGeneratedCount(token:str):
    db = client["Redirects"] # from redirects we are trying to get email on which the given token(event token) is registered
    collection = db["secrets"]
    tokens = (await collection.find({}, {"_id": 0}).to_list(None))[0]["tokens"]
    for tokenn in tokens:
        if tokenn[0] == token: # here tokenn[0] is event token like [event_token, email]
            db2 = client["Clients"] # from Clients we are trying to get the event_id (ObjectID of event)
            collection2 = db2[tokenn[1]]  # here tokenn[1] is email like [event_token, email]
            tokens_ids = (await collection2.find({}, {"_id": 0}).to_list(None))[0]["event_ids"] # token_ids contains [event_id, event_name, event_token]
            await collection2.update_one(
                {"email":tokenn[1]},
                {"$inc": {"total_attendies": 1}}
            )
            for token_id in tokens_ids: 
                if token_id[2] == token: # here token_id[2] is event token
                    db3 = client["Events"]
                    collection3 = db3[tokenn[1]] # here tokenn[1] is email
                    await collection3.update_one(
                        {"_id": ObjectId(token_id[0])}, # here token_id[0] is event_id
                        {"$inc": {"total_generated_tickets": 1}}
                    )
                    break
                else:
                    continue
                    
async def updateEventAttendeesCount(token:str):
    db = client["Redirects"]
    collection = db["secrets"]

    tokens = (await collection.find({}, {"_id": 0}).to_list(None))[0]["tokens"]

    for tokenn in tokens:
        if tokenn[0] == token:
            db2 = client["Clients"]
            collection2 = db2[tokenn[1]]
            tokens_ids = (await collection2.find({}, {"_id": 0}).to_list(None))[0]["event_ids"]
            for token_id in tokens_ids: 
                if token_id[2] == token: # here token_id[2] is event token
                    db3 = client["Events"]
                    collection3 = db3[tokenn[1]] # here tokenn[1] is email
                    await collection3.update_one(
                        {"_id": ObjectId(token_id[0])}, # here token_id[0] is event_id
                        {"$inc": {"total_attendies": 1}}
                    )
                    break
                else:
                    continue