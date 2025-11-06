from config.ticketsDB import client


async def verify_ticket_admin(ticket:str):
    db = client["Tickets"]
    tickets = await db.list_collection_names()
    if ticket in tickets:
        collection = db[ticket]
        ticket_data = await collection.find({}, {"_id": 0}).to_list(None)
        if not ticket_data[0]["attended"] :
            await collection.update_one(
                {"ticket_id":ticket},
                {"$set":{"attended":True}}
            )
            return True
        else:
            return False
    else:
        return False
    

async def get_ticket_info(ticket:str):
    db = client["Tickets"]
    tickets = await db.list_collection_names()
    if ticket in tickets:
        collection = db[ticket]
        ticket_data = await collection.find({}, {"_id": 0}).to_list(None)
        if not ticket_data[0]["attended"] :
            valid = True
        else:
            valid = False

        name = ticket_data[0]["name"]
        email = ticket_data[0]["email"]
        phone = ticket_data[0]["phone"]

        tic_details = {
            "name" : name,
            "email" : email,
            "phone" : phone,
            "valid" : valid
        }
        return tic_details
    else:
        return False
    

async def just_check_ticket(ticket:str):
    db = client["Tickets"]
    tickets = await db.list_collection_names()

    if ticket in tickets:
        return True
    else:
        return False