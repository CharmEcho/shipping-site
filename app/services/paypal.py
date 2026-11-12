import base64
import requests
from flask import current_app

PAYPAL_API = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com",
}

def get_access_token():
    client_id = current_app.config.get("PAYPAL_CLIENT_ID")
    secret = current_app.config.get("PAYPAL_SECRET")
    mode = current_app.config.get("PAYPAL_MODE", "sandbox")

    if not client_id or not secret:
        raise RuntimeError("PayPal credentials not configured")

    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()

    response = requests.post(
        f"{PAYPAL_API[mode]}/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=15,
    )

    response.raise_for_status()
    return response.json()["access_token"]
