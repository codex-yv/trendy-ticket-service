from config.ticketsDB import client
from utils.adminPuts import updateTicketGeneratedCount
from bson.objectid import ObjectId

async def insert_ticket(Data:dict, collection_name:str, ticket_id:str): # /see project schemas in adminProjectSchemas.py
    db = client['Tickets']
    collection = db[collection_name] # collection_name is the event token
    
    result = await collection.insert_one(Data)

    ticket_db_id = str(result.inserted_id)

    db2 = client["TicVer"]
    collection2 = db2["ticMaps"]
    insert_data = {
        collection_name: ticket_db_id
    }
    await collection2.update_one({"_id": ObjectId("6910e37a2b3d2191a187a5d6")}, {"$set":{"mapping": insert_data}})

    value = await collection2.find({}, {"_id": 0}).to_list(None)
    id_mapping = value[0]["id_mapping"]
    try:
        ticket_id_list = id_mapping[collection_name]
        ticket_id_list.append(ticket_id)
        id_mapping[collection_name] = ticket_id_list
    except:
        id_mapping[collection_name] = [ticket_id]

    await collection2.update_one({"_id": ObjectId("6910e37a2b3d2191a187a5d6")}, {"$set":{"id_mapping": id_mapping}})

    await updateTicketGeneratedCount(collection_name)
    return True

    
