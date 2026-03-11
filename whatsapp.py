import os
import requests


WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"


def send_whatsapp_message(message: str) -> dict:
    """
    Send a text message via the WhatsApp Business Cloud API.

    Returns:
        API response dict.
    """
    phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    access_token = os.environ["WHATSAPP_ACCESS_TOKEN"]
    recipient = os.environ["WHATSAPP_RECIPIENT_NUMBER"]

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # WhatsApp text messages have a 4096 char limit — truncate if needed.
    if len(message) > 4000:
        message = message[:3997] + "..."

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()
