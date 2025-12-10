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
    razorpay_key_id:str
    razorpay_key_secret:str

class OTP(BaseModel):
    email:str

class TicketScan(BaseModel):
    key: str
    token:str