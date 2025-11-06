from config.ticketsDB import client


async def insert_ticket(Data:dict): # /see project schemas in adminProjectSchemas.py
    db = client['Tickets']
    tickets = await db.list_collection_names()

    if Data["ticket_id"] not in tickets:
        collection = db[Data["ticket_id"]]
        await collection.insert_one(Data)
        return True
    else:
        return False
    
