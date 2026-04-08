import requests
import base64
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import MpesaConfiguration
import logging

logger = logging.getLogger(__name__)

def get_mpesa_config():
    config = MpesaConfiguration.objects.first()
    if config:
        return config
    # Fallback to settings if no DB config exists
    class FallbackConfig:
        consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        short_code = getattr(settings, 'MPESA_SHORTCODE', '174379')
        passkey = getattr(settings, 'MPESA_PASSKEY', '')
        is_sandbox = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox') == 'sandbox'
    return FallbackConfig()

def get_mpesa_access_token():
    config = get_mpesa_config()
    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if not config.is_sandbox:
        api_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        res = requests.get(api_url, auth=(consumer_key, consumer_secret), timeout=10)
        if res.status_code != 200:
            print(f"M-Pesa Token Error: {res.status_code} - {res.text}")
        res.raise_for_status()
        return res.json().get('access_token')
    except Exception as e:
        print(f"Error getting M-Pesa token: {e}")
        return None


def initiate_stk_push(phone_number, amount, callback_url, order_id):
    access_token = get_mpesa_access_token()
    if not access_token:
        return None

    config = get_mpesa_config()
    business_short_code = config.short_code
    passkey = config.passkey
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()


    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(float(amount)), # Ensure it's a solid integer even if passed as decimal
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"Order_{order_id}",
        "TransactionDesc": f"Payment for Order {order_id}"
    }

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    if not config.is_sandbox:
        api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    try:
        logger.info(f"Initiating STK Push for {phone_number} amount {amount}")
        res = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response_data = res.json()
        
        if res.status_code != 200:
            logger.error(f"M-Pesa STK Push ERROR: {res.status_code} - {res.text}")
        else:
            logger.info(f"M-Pesa STK Push SUCCESS: {response_data}")
            
        return response_data
    except Exception as e:
        logger.exception(f"Exception during STK push: {e}")
        return None

