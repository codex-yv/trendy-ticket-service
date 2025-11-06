from pydantic import BaseModel

class Ticket(BaseModel):
    ticket_id:str
    