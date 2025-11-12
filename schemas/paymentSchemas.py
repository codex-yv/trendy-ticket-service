from pydantic import BaseModel

class Payment(BaseModel):
    name:str
    email:str
    phone:str

class NoPay(BaseModel):
    name:str
    email:str
    phone:str