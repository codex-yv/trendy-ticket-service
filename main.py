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

from schemas.ticketSchema import Ticket
from schemas.paymentSchemas import Payment
from schemas.emailSchemas import Email, OTP
from schemas.amountSchemas import Amount

from security.encrypyAmt import encryptt
from config.payment_config import key_id, key_seceret
from utils.tickPost import insert_ticket
from utils.trickGet import verify_ticket_admin, just_check_ticket, get_ticket_info

from utils.general import get_amount, share_ticket
from utils.IST import ISTdate, ISTTime

templates = Jinja2Templates(directory="templates")

RAZORPAY_KEY_ID = key_id
RAZORPAY_KEY_SECRET = key_seceret

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key="qwertyuiopasdfghjkl@#$%RTYU", same_site="none", https_only=True, max_age=3600)
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
        # print(data)
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
async def payment_success(request:Request):
    amount = request.cookies.get("session_amount")
    email = request.session.get("email")
    return templates.TemplateResponse("unsuccess.html", {"request":request, "email":email, "amount":amount})

@app.get('/generate/ticket')
async def payment_success(request:Request):
    ticket_id = request.session.get("ticket")
    ticket_details = await get_ticket_info(ticket=ticket_id)
    email = ticket_details["email"]
    name = ticket_details["name"]
    phone = ticket_details["phone"]
    valid = ticket_details["valid"]
    return templates.TemplateResponse("tickets.html", {"request":request, "ticket_id":ticket_id, "valid":valid, "name":name, "email":email, "phone":phone})

@app.get("/admin/verify")
async def ticket_verification_page(request:Request):
    return templates.TemplateResponse("verification.html", {"request":request})

# return templates.TemplateResponse("verification.html", {"request":request, "ticket_id":ticket_id, "valid":true, "name":name, "email":email, "phone":phone})


@app.post("/payment")
async def tts_payment(request: Request, response: Response, data: Amount):
    idd = str(uuid.uuid4())
    key, token = await encryptt(amount=str(data.amount))
    
    url = idd + "#" + token.decode() + "#" + key.decode()
    safe_url = quote(url, safe="")
    
    # Check if request is from fetch (has Accept: application/json header)
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header:
        # Return JSON response with redirect URL for fetch requests
        redirect_url = f"/{safe_url}"
        json_response = JSONResponse(content={"redirect_url": redirect_url, "success": True})
        json_response.set_cookie(key="session_amount", value=str(data.amount), httponly=True, max_age=60*60)
        return json_response
    else:
        # Return redirect response for direct form submissions
        response =  RedirectResponse(url=f"/{safe_url}", status_code=303)
        response.set_cookie(key="session_amount", value=str(data.amount), httponly=True, max_age=60*60)
        return response

@app.post("/send-otp")
async def send_otp(request:Request, email:Email = Body(...)):
    # print(f"Email: {email.email}")
    request.session["otp"] = "12345"
    # print(f"Stored OTP in session: {request.session.get('otp')}")
    # print(f"Session ID: {request.session}")
    return JSONResponse(content={"success": True, "message": f"OTP sent to {email.email}"})

@app.post("/verify-otp")
async def verify_otp(request:Request, otp:OTP = Body(...)):
    stored_otp = request.session.get("otp")
    # print(f"Retrieved OTP from session: {stored_otp}")
    # print(f"Received OTP from request: {otp.otp}")
    # print(f"Session ID: {request.session}")
    
    if stored_otp == otp.otp:
        return JSONResponse(content={"success": True, "message": "OTP verified successfully"})
    else:
        return JSONResponse(content={"success": False, "message": "Invalid OTP"}, status_code=400)


@app.post('/order')
def create_order(request:Request, payment:Payment):
    # Create an order with Razorpay
    amount = request.cookies.get("session_amount")  # Amount in paise (e.g., ₹500)
    currency = "INR"

    request.session["name"] = payment.name
    request.session["email"] = payment.email
    request.session["phone"] = payment.phone
    
    order_data = {
        "amount": int(float(amount)*100),
        "currency": currency
    }

    razorpay_order = razorpay_client.order.create(data=order_data)
    # print(razorpay_order['id'])
    return {"order_id": razorpay_order['id'], "amount": amount}

@app.post('/verify')
async def verify_signature(request: Request):
    # Data from Razorpay Checkout
    form = await request.form()
    payment_id = form.get("razorpay_payment_id")
    order_id = form.get("razorpay_order_id")
    signature = form.get("razorpay_signature")

    # print()
    # print(order_id)
    # print(signature)
    # Verify signature
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })
        name = request.session.get("name")
        email = request.session.get("email")
        phone = request.session.get("phone")
        amount = request.cookies.get("session_amount")
        time = f"{ISTdate()} {ISTTime()}"

        inserting_data = {
            "name":name,
            "email":email,
            "phone":phone,
            "amount":amount,
            "attended":False,
            "ticket_id":order_id,
            "payment_id":payment_id,
            "signature":signature,
            "payment_time":time,
            "attending_time":""
        }
        is_inserted = await insert_ticket(Data=inserting_data)
        await share_ticket(ticket=order_id, email=email)
        
        if is_inserted:
            return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page
        else:
            # generate your own ticket_id
            print("EROR")
            
    except razorpay.errors.SignatureVerificationError:
        return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page

@app.post("/verify-ticket")
async def verify_ticket(request:Request, ticket:Ticket):
    # print(f"Verifying ticket: {ticket.ticket_id}")
    
    is_valid = await verify_ticket_admin(ticket=ticket.ticket_id)  # Replace with actual validation logic
    
    return JSONResponse(content={"valid": is_valid})

@app.post("/verify-ticket-id")
async def generate_ticket(request:Request, ticket_id:Ticket):
    is_ticket = await just_check_ticket(ticket=ticket_id.ticket_id)
    request.session["ticket"] = ticket_id.ticket_id
    if not is_ticket:
        return JSONResponse(content={"success": is_ticket, "message": "Invalid Ticket ID"})
    else:
        return RedirectResponse(url = '/generate/ticket',  status_code=HTTP_303_SEE_OTHER)

@app.get("/generate/ticket/event")
async def generate_ticket_event(request:Request):
    return templates.TemplateResponse("generate.html", {"request":request})





