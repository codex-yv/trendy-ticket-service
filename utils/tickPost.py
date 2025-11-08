from config.ticketsDB import client
from utils.adminPuts import updateTicketGeneratedCount

async def insert_ticket(Data:dict, collection_name:str): # /see project schemas in adminProjectSchemas.py
    db = client['Tickets']
    collection = db[collection_name]
    
    await collection.insert_one(Data)
    await updateTicketGeneratedCount(collection_name)
    return True

    
