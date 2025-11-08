import token
from pydantic import BaseModel
from razorpay.resources import payment

from config.payment_config import key_id

class RedirectTTS(BaseModel):
    amount:float
    payment:bool
    token:str
    key:str
