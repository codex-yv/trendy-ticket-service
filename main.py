from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body, HTTPException, status, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
import secrets
import uuid
from urllib.parse import quote
import razorpay

from schemas.paymentSchemas import Payment
from schemas.emailSchemas import Email, OTP
from schemas.amountSchemas import Amount

from security.encrypyAmt import encryptt
from utils.general import get_amount

templates = Jinja2Templates(directory="templates")

RAZORPAY_KEY_ID = "rzp_test_jMpRm1HDX5ZT4x"
RAZORPAY_KEY_SECRET = "PERAVYmOCKh4ZygDuRzEJWzi"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key="qwertyuiopasdfghjkl@#$%RTYU", same_site="lax", https_only=False, max_age=3600)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "123")
    correct_password = secrets.compare_digest(credentials.password, "123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(user: str = Depends(get_current_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure API Docs")


@app.api_route("/", methods=["HEAD"], operation_id="welcome_get")
async def welcome_head():
    return {"Message": "Ok"}

@app.get("/{info}")
async def dashboard(request: Request, info: str = None):
    amount = await get_amount(mesh=info)
    if amount:
        data = request.cookies.get("session_amount")
        print(data)
        return templates.TemplateResponse(
            "payments.html",
            {"request": request, "amount": str(amount),  "key_id":RAZORPAY_KEY_ID}
        )
    else:
        return templates.TemplateResponse("success.html", {"request":request})
    
@app.get('/success/payment')
def payment_success(request:Request):
    amount = request.cookies.get("session_amount")
    email = request.session.get("email")
    return templates.TemplateResponse("success.html", {"request":request, "email":email, "amount":amount})

@app.get('/unsuccess/payment')
def payment_success(request:Request):
    amount = request.cookies.get("session_amount")
    email = request.session.get("email")
    return templates.TemplateResponse("unsuccess.html", {"request":request, "email":email, "amount":amount})

@app.post("/payment")
async def tts_payment(request: Request, response: Response, data: Amount):
    idd = str(uuid.uuid4())
    key, token = await encryptt(amount=str(data.amount))
    
    url = idd + "#" + token.decode() + "#" + key.decode()
    safe_url = quote(url, safe="")
    response =  RedirectResponse(url=f"/{safe_url}", status_code=303)
    response.set_cookie(key="session_amount", value=str(data.amount), httponly=True, max_age=60*60)
    return response

@app.post("/send-otp")
async def send_otp(request:Request, email:Email = Body(...)):
    print(f"Email: {email.email}")
    request.session["otp"] = "12345"
    print(f"Stored OTP in session: {request.session.get('otp')}")
    print(f"Session ID: {request.session}")
    return JSONResponse(content={"success": True, "message": f"OTP sent to {email.email}"})

@app.post("/verify-otp")
async def verify_otp(request:Request, otp:OTP = Body(...)):
    stored_otp = request.session.get("otp")
    print(f"Retrieved OTP from session: {stored_otp}")
    print(f"Received OTP from request: {otp.otp}")
    print(f"Session ID: {request.session}")
    
    if stored_otp == otp.otp:
        return JSONResponse(content={"success": True, "message": "OTP verified successfully"})
    else:
        return JSONResponse(content={"success": False, "message": "Invalid OTP"}, status_code=400)


@app.post('/order')
def create_order(request:Request, payment:Payment):
    # Create an order with Razorpay
    amount = request.cookies.get("session_amount")  # Amount in paise (e.g., ₹500)
    currency = "INR"
    # print(payment.name)
    # print(payment.email)
    # print(payment.phone)

    request.session["name"] = payment.name
    request.session["email"] = payment.email
    request.session["phone"] = payment.phone
    
    order_data = {
        "amount": int(float(amount)*100),
        "currency": currency
    }
    print()
    print(order_data)
    print()
    razorpay_order = razorpay_client.order.create(data=order_data)
    print(razorpay_order['id'])
    return {"order_id": razorpay_order['id'], "amount": amount}

@app.post('/verify')
async def verify_signature(request: Request):
    # Data from Razorpay Checkout
    form = await request.form()
    payment_id = form.get("razorpay_payment_id")
    order_id = form.get("razorpay_order_id")
    signature = form.get("razorpay_signature")

    print(payment_id)
    print(order_id)
    print(signature)
    # Verify signature
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })
        return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page
    except razorpay.errors.SignatureVerificationError:
        return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page

@app.get("/admin/verify")
async def ticket_verification_page(request:Request):
    return templates.TemplateResponse("verification.html", {"request":request})

@app.post("/guess")
async def get_guess(request:Request):
    data = request.cookies.get("session_amount")
    print(data)



