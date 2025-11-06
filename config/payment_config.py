from dotenv import load_dotenv
import os

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_seceret = os.getenv("RAZORPAY_KEY_SECRET")