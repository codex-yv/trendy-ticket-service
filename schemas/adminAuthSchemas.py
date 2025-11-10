from pydantic import BaseModel

class Login(BaseModel):
    email: str
    password: str

class Signup(BaseModel):
    fullname: str
    email: str
    password: str
    phone: str
    otp: str

class OTP(BaseModel):
    email:str

class TicketScan(BaseModel):
    key: str
    token:str