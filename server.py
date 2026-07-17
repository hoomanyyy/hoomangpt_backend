from pdf_reader import read_pdf
from model import generate_response
import requests
import os
import uvicorn
from dotenv import load_dotenv



load_dotenv()

NOW_API_KEY = os.getenv(
    "NOW_API_KEY"
)

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form,
    Request
)

from fastapi.middleware.cors import CORSMiddleware


from database.mysql import (
    user_login,
    user_signup,
    use_credit,
    get_user_plan,
    get_daily_limit,
    get_usage,
    change_email,
    change_password,
    upgrade_plan
)


app = FastAPI()



app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)





# ==========================
# PDF SUMMARY
# ==========================


@app.post("/api/generate_response")
async def generate_model_response(

    file: UploadFile = File(...),

    user_id:int = Form(...)

):


    # check daily limit

    if not use_credit(user_id):

        raise HTTPException(

            status_code=403,

            detail="Daily limit reached"

        )



    text = read_pdf(
        file.file
    )



    print(
        "PDF length:",
        len(text)
    )



    response = generate_response(
        text
    )



    return {


        "summary":response,


        "context":text,


        "chars":len(text)

    }





# ==========================
# LOGIN
# ==========================


@app.post("/api/login")
def login(data:dict):


    email=data["email"]

    password=data["password"]



    result=user_login(

        email,

        password

    )



    if not result:


        raise HTTPException(

            status_code=401,

            detail="Wrong email or password"

        )



    return result





# ==========================
# SIGNUP
# ==========================


@app.post("/api/signup")
def signup(data:dict):


    result=user_signup(

        data["name"],

        data["email"],

        data["password"]

    )


    if not result:


        raise HTTPException(

            status_code=400,

            detail="Signup failed"

        )



    return result





# ==========================
# GET PLAN
# ==========================


@app.post("/api/getPlan")
def getPlan(data:dict):

    user_id=data["id"]


    plan=get_user_plan(
        user_id
    )


    return {

        "plan":plan

    }




# ==========================
# GET USAGE STATUS
# ==========================


@app.post("/api/getUsage")
def getUsage(data:dict):


    user_id=data["id"]



    plan=get_user_plan(
        user_id
    )


    limit=get_daily_limit(
        user_id
    )



    used=get_usage(
        user_id
    )



    return {


        "plan":plan,


        "used":used,


        "limit":limit,


        "remaining":max(
            limit-used,
            0
        )

    }


@app.get("/api/health")
def health():

    return {
        "status":"online",
        "model":"Qwen2"
    }


@app.post("/api/change-email")
def update_email(data:dict):

    user_id = data["user_id"]
    new_email = data["email"]


    result = change_email(
        user_id,
        new_email
    )


    if not result:

        raise HTTPException(
            status_code=400,
            detail="این ایمیل قبلا استفاده شده است"
        )


    return {
        "message":"Email updated",
        "email":new_email
    }



@app.post("/api/change-password")
def update_password(data:dict):

    user_id = data["user_id"]
    password = data["password"]


    change_password(
        user_id,
        password
    )


    return {
        "message":"Password updated"
    }

# ==========================
# BILLING
# ==========================


@app.post("/api/create-payment")
def create_payment(data:dict):


    user_id=data["user_id"]



    payload={


        "price_amount":4,


        "price_currency":"usd",


        "order_id":str(user_id),


        "order_description":
        "NoteFinder PRO",



        "success_url":
        "http://localhost:5173/dashboard",



        "cancel_url":
        "http://localhost:5173/billing",



        "ipn_callback_url":
        "https://YOUR-NGROK-URL.ngrok-free.app/api/payment-webhook"



    }



    headers={


        "x-api-key":NOW_API_KEY,


        "Content-Type":
        "application/json"


    }



    response=requests.post(


        "https://api.nowpayments.io/v1/invoice",


        json=payload,


        headers=headers


    )




    if response.status_code != 200:


        raise HTTPException(

            status_code=400,

            detail=response.text

        )



    return response.json()






@app.post("/api/payment-webhook")
async def payment_webhook(
    request:Request
):


    data=await request.json()



    print("================")
    print(data)
    print("================")



    status=data.get(
        "payment_status"
    )


    user_id=data.get(
        "order_id"
    )



    if status=="finished":


        upgrade_plan(

            int(user_id),

            "PRO"

        )



    return {


        "success":True

    }


if __name__=="__main__":


    uvicorn.run(

        "server:app",

        host="0.0.0.0",

        port=8000,

        reload=True

    )