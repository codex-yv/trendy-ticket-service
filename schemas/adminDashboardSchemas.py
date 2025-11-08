from pydantic import BaseModel

class Useless(BaseModel):
    x:str

class Hosting(BaseModel):
    event_name:str
    company_name:str
    event_location:str
    start_date:str
    end_date:str
    ticket_cost:str
    expiry:str
    ticket_limit:str
    event_token:str