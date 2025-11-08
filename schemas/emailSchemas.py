from pydantic import BaseModel

class Email(BaseModel):
    email:str

class OTPe(BaseModel):
    otp:str