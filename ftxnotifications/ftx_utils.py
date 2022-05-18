import hmac
import os
import time

import requests as requests
from dotenv import load_dotenv
from requests import Request

load_dotenv()

API_KEY = os.getenv("FTX_API_KEY")
API_SECRET = os.getenv("FTX_API_SECRET")
SUB_ACCOUNT = os.getenv("FTX_SUB_ACCOUNT")

session = requests.Session()

API_URL = "https://ftx.com/api"


def sign_request(request: Request, subaccount):
    ts = int(time.time() * 1000)
    prepared = session.prepare_request(request)
    if prepared.body:
        signature = f"{ts}{prepared.method}{prepared.path_url}{prepared.body.decode()}"
    else:
        signature = f"{ts}{prepared.method}{prepared.path_url}"
    signature_payload = signature.encode()
    signature = hmac.new(API_SECRET.encode(), signature_payload, "sha256").hexdigest()

    prepared.headers["FTX-SIGN"] = signature
    prepared.headers["FTX-TS"] = str(ts)
    prepared.headers["FTX-KEY"] = API_KEY
    if subaccount and subaccount != "Main Account":
        prepared.headers["FTX-SUBACCOUNT"] = subaccount
    return prepared


def get_endpoint(endpoint, subaccount):
    request = Request("GET", f"{API_URL}/{endpoint}")
    return session.send(sign_request(request, subaccount), timeout=10).json()["result"]


def get_notifications():
    return get_endpoint("notifications/get_for_user", SUB_ACCOUNT)
