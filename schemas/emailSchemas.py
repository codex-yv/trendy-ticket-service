from pydantic import BaseModel

class Email(BaseModel):
    email:str

class OTP(BaseModel):
    otp:str