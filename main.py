import email
from this import d
from fastapi import FastAPI, Request, Form, Body, HTTPException, status, Depends, Response
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
from schemas.emailSchemas import Email, OTPe
from schemas.RedirectSchemas import RedirectTTS
from schemas.adminAuthSchemas import Login, Signup, OTP, TicketScan
from schemas.adminDashboardSchemas import Useless, Hosting

from security.encrypyAmt import encryptt
from config.payment_config import key_id, key_seceret

from utils.tickPost import insert_ticket
from utils.trickGet import verify_ticket_admin, just_check_ticket, get_ticket_info

from utils.adminGets import checkAdmin, checkAdminPassword, getAdminDashboardData, getAdminSecurityData, getAdminEvents, getEventAttendees, checkRedirectTTS, verifyAdminforScan, checkTokenExpiry
from utils.adminPosts import createNewAdmin, hostEvent
from utils.adminPuts import updateAdminKey, deteleEvent, updateActiveEventsCounts

from utils.general import get_amount, share_ticket, generate_event_token, send_otp
from utils.IST import ISTdate, ISTTime
from utils.redirectCURD import update_json, get_value

templates = Jinja2Templates(directory="templates")
templates_admin = Jinja2Templates(directory="templates/admin")

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
    is_key = await get_value(file_path="database/redirectTTS.json", key=info)
    if is_key:
        amount = is_key["amount"]
        token = is_key["token"]
        if amount and token:
            request.session["session_amount"] = amount
            request.session["token"] = token
            return templates.TemplateResponse(
                "payments.html",
                {"request": request, "amount": str(amount),  "key_id":RAZORPAY_KEY_ID}
            )
    else:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    
@app.get('/success/payment')
def payment_success(request:Request):
    amount = request.session.get("session_amount")
    email = request.session.get("email")
    if amount and email:
        return templates.TemplateResponse("success.html", {"request":request, "email":email, "amount":amount})
    else:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@app.get('/unsuccess/payment')
async def payment_success(request:Request):
    amount = request.session.get("session_amount")
    email = request.session.get("email")
    if amount and email:
        return templates.TemplateResponse("unsuccess.html", {"request":request, "email":email, "amount":amount})
    else:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@app.get('/generate/ticket')
async def payment_success(request:Request):
    ticket_id = request.session.get("ticket")
    if ticket_id:
        ticket_details = await get_ticket_info(ticket=ticket_id)
        email = ticket_details["email"]
        name = ticket_details["name"]
        phone = ticket_details["phone"]
        valid = ticket_details["valid"]
        expiry = ticket_details["expiry"]
        event_name = ticket_details["event_name"]
        event_loc = ticket_details["eve_location"]
        event_date = ticket_details["event_start"]
        return templates.TemplateResponse("tickets.html", {"request":request, "ticket_id":ticket_id, "valid":valid, "name":name, "email":email, "phone":phone, "expiry": expiry, "event_loc":event_loc.title(), "event_date":event_date, "event_name":event_name.title()})

    else:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/verify") # add cokkie access
async def ticket_verification_page(request:Request):
    print("I am here!")
    admin = request.cookies.get("session_admin_scan_key")
    token = request.cookies.get("session_admin_scan_token")
    if admin and token:
        print("VALID TOKEN")
        return templates.TemplateResponse("verification.html", {"request":request})
    else:
        print("INVALID TOKEN")
        return RedirectResponse(url="/admin/scan", status_code=HTTP_303_SEE_OTHER)

@app.get("/admin/scan") 
async def admin_scan(request:Request):
    return templates.TemplateResponse("adminscanverification.html", {"request":request})

@app.post("/payment")
async def tts_payment(request: Request, response: Response, data: RedirectTTS):
    is_redirect = await checkRedirectTTS(key=data.key, token=data.token)
    print(is_redirect)
    if is_redirect:
        is_expired = await checkTokenExpiry(token=data.token)
        if not is_expired:
            redirect_data = {"token": data.token, "amount": data.amount}

            idd = str(uuid.uuid4())

            file_path = "database/redirectTTS.json"
            await update_json(file_path=file_path, key=idd, value=redirect_data)
            
            safe_url = quote(idd, safe="")
            
            # Check if request is from fetch (has Accept: application/json header)
            accept_header = request.headers.get("accept", "")
            if "application/json" in accept_header:
                # Return JSON response with redirect URL for fetch requests
                redirect_url = f"/{safe_url}"
                json_response = JSONResponse(content={"redirect_url": redirect_url, "success": True})
                return json_response
            else:
                response =  RedirectResponse(url=f"/", status_code=303)
                return response
        else:
            return JSONResponse(content={"success": False, "message": "Event Token is expired!"}, status_code=400)
    else:
        return JSONResponse(content={"success": False, "message": "Invalid key or token"}, status_code=400)

@app.post("/send-otp")
async def send_OTP(request:Request, email:Email = Body(...)):
    sended_otp = await send_otp(email=email.email)
    request.session["otp"] = sended_otp
    return JSONResponse(content={"success": True, "message": f"OTP sent to {email.email}"})

@app.post("/verify-otp")
async def verify_otp(request:Request, otp:OTPe = Body(...)):
    stored_otp = request.session.get("otp")
    
    if str(stored_otp) == str(otp.otp):
        return JSONResponse(content={"success": True, "message": "OTP verified successfully"})
    else:
        return JSONResponse(content={"success": False, "message": "Invalid OTP"}, status_code=400)


@app.post('/order')
def create_order(request:Request, payment:Payment):
    # Create an order with Razorpay
    amount = request.session.get("session_amount")  # Amount in paise (e.g., ₹500)
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
        amount = request.session.get("session_amount")
        token = request.session.get("token")
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
        is_inserted = await insert_ticket(Data=inserting_data, collection_name=token, ticket_id=order_id)
        await share_ticket(ticket=order_id, email=email)
        
        if is_inserted:
            return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page
        else:
            # generate your own ticket_id
            print("EROR")
            
    except razorpay.errors.SignatureVerificationError:
        return RedirectResponse(url = '/success/payment',  status_code=HTTP_303_SEE_OTHER)  # Redirect to success page


@app.post("/verify-ticket") # ticket validation via QR scannig
async def verify_ticket(request:Request, ticket:Ticket):
    token = request.cookies.get("session_admin_scan_token")
    is_valid = await verify_ticket_admin(ticket=ticket.ticket_id, token=token) 
    
    return JSONResponse(content={"valid": is_valid})
   

@app.post("/admin/verify/scan")
async def admin_verify_scan(request:Request, admin:TicketScan, response:Response):
    
    val = await verifyAdminforScan(token=admin.token, key=admin.key) 
    if val == -1:
        return 1
    elif val == 0:
        return 0
    else:
        response = RedirectResponse(url = '/admin/verify',  status_code=HTTP_303_SEE_OTHER)
        response.set_cookie(key = "session_admin_scan_key", value=admin.key, httponly=True, max_age=60*60*24*7)
        response.set_cookie(key = "session_admin_scan_token", value=admin.token, httponly=True, max_age=60*60*24*7)
        return response
    
    

@app.get("/generate/ticket/event") # a simple form to submit the ticket tID
async def generate_ticket_event(request:Request):

    return templates.TemplateResponse("generate.html", {"request":request})


@app.post("/verify-ticket-id") # if ticket id is valid them it will generate ticket page.
async def generate_ticket(request:Request, ticket_id:Ticket):
    is_ticket = await just_check_ticket(ticket=ticket_id.ticket_id)
    request.session["ticket"] = ticket_id.ticket_id
    if not is_ticket:
        return JSONResponse(content={"success": is_ticket, "message": "Invalid Ticket ID"})
    else:
        return RedirectResponse(url = '/generate/ticket',  status_code=HTTP_303_SEE_OTHER)




# =======================================================ADMIN Setup===================================================================

@app.get("/")
async def get_admin_page(request:Request):
    admin = request.cookies.get("session_user_admin")

    if admin:
        return RedirectResponse(url = '/admin/dashboard')
    else:
        return templates_admin.TemplateResponse("index.html", {"request":request})

@app.get( "/admin/login")
async def admin_login(request:Request):
    admin = request.cookies.get("session_user_admin")
    if admin:
        return RedirectResponse(url = '/admin/dashboard',  status_code=HTTP_303_SEE_OTHER)
    return templates_admin.TemplateResponse("login.html", {"request":request})

@app.get("/admin/signup")
async def admin_signup(request:Request):
    admin = request.cookies.get("session_user_admin")
    if admin:
        return RedirectResponse(url = '/admin/dashboard',  status_code=HTTP_303_SEE_OTHER)  
    return templates_admin.TemplateResponse("signup.html", {"request":request})

@app.get("/admin/dashboard")
async def admin_dashboard(request:Request):
    admin = request.cookies.get("session_user_admin")
    print(admin)
    if admin:
        await updateActiveEventsCounts(email=admin)
        admin_dashboard_data = await getAdminDashboardData(email=admin)
        totoal_active_events = admin_dashboard_data["total_active_events"]
        total_events = admin_dashboard_data["total_events"]
        total_users = admin_dashboard_data["total_attendies"]
        recent_events = admin_dashboard_data["recent_events"]

        return templates_admin.TemplateResponse("dashboard.html", {"request":request, "recent_events":recent_events, "total_events":total_events, "total_users":total_users, "totoal_active_events":totoal_active_events})
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/send-otp")
async def admin_send_otp(request:Request, email:OTP):
    sended_otp = await send_otp(email=email.email)
    request.session["admin_otp"] = sended_otp
    return True

@app.post("/admin/signup")
async def admin_signup(request:Request, data:Signup):
    sended_otp = request.session.get("admin_otp")
    if str(data.otp) != str(sended_otp): # real otp will be done here instead of constant
        return 0
    else:
        admin_exist = await checkAdmin(email=data.email)
        if not admin_exist:
            await createNewAdmin(admin_data=data)
            return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)
        else:
            return -1

@app.post("/admin/login")
async def admin_login(request:Request, data:Login, response: Response):
    admin_exist = await checkAdmin(email=data.email)
    if admin_exist:
        is_password = await checkAdminPassword(email=data.email, password=data.password)
        if is_password:
            response =  RedirectResponse(url = '/admin/dashboard',  status_code=HTTP_303_SEE_OTHER)
            response.set_cookie(key="session_user_admin", value=data.email, httponly=True, max_age=60*60*24*7)

            return response
        else:
            return -1
    else:
        return 0

@app.post("/admin/ui/dashboard")
async def admin_dashboard(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        await updateActiveEventsCounts(email=admin)
        admin_data_dict = await getAdminDashboardData(email=admin)
        return admin_data_dict
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)


@app.post("/admin/ui/events")
async def admin_events(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        await updateActiveEventsCounts(email=admin)
        eventss = await getAdminEvents(email=admin)
        print(eventss)
        return eventss
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/events/attendees")
async def admin_event_attendees(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        attendees = await getEventAttendees(email=admin, event_id=data.x)
        return attendees
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/security")
async def admin_security(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        admin_data_dict = await getAdminSecurityData(email=admin)
        return admin_data_dict
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/security/api_key")
async def admin_api_key(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        new_key = await updateAdminKey(email=admin)
        return new_key
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/security/event_token")
async def admin_event_token(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        await deteleEvent(email=admin, event_id=data.x)
        
        return True
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)


@app.post("/admin/ui/host-event")
async def admin_host_event_section(request:Request, data:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        event_token = await generate_event_token()
        request.session["event_token"] = event_token
        return event_token
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/host-event/host")
async def admin_host_event(request:Request, hosting:Hosting):
    admin = request.cookies.get("session_user_admin")
    if admin:
        if request.session.get("event_token") == hosting.event_token:
            await hostEvent(hosting=hosting, email=admin)
            return True 
        else:
            return False
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)

@app.post("/admin/ui/logout")
async def admin_logout(request:Request, response:Response, x:Useless):
    admin = request.cookies.get("session_user_admin")
    if admin:
        response = RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)
        response.delete_cookie("session_user_admin")
        return response
    else:
        return RedirectResponse(url = '/admin/login',  status_code=HTTP_303_SEE_OTHER)