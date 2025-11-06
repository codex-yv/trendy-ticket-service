from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body, HTTPException, status, Depends
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

from schemas.amountSchemas import Amount
from security.encrypyAmt import encryptt
from utils.general import get_amount

templates = Jinja2Templates(directory="templates")

RAZORPAY_KEY_ID = "rzp_test_jMpRm1HDX5ZT4x"
RAZORPAY_KEY_SECRET = "PERAVYmOCKh4ZygDuRzEJWzi"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key="qwertyuiopasdfghjkl@#$%RTYU", same_site="none", https_only=False)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
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
    am = await get_amount(mesh=info)
    if am:
        amount = 100
        return templates.TemplateResponse(
            "payments.html",
            {"request": request, "amount": str(am),  "key_id":RAZORPAY_KEY_ID}
        )
    else:
        return templates.TemplateResponse("success.html", {"request":request})
    
@app.post("/payment")
async def tts_payment(request: Request, data: Amount):
    idd = str(uuid.uuid4())
    key, token = await encryptt(amount=str(data.amount))

    url = idd + "#" + token.decode() + "#" + key.decode()
    safe_url = quote(url, safe="")
    print(url)
    return RedirectResponse(url=f"/{safe_url}", status_code=303)
