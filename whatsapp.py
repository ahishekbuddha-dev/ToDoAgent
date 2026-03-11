import os
import requests


WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"


def _normalize_number(number: str) -> str:
    """Ensure number has + prefix and no spaces."""
    number = number.replace(" ", "")
    if not number.startswith("+"):
        number = f"+{number}"
    return number


def send_whatsapp_message(message: str) -> dict:
    """
    Send a text message via the WhatsApp Business Cloud API.

    Returns:
        API response dict.
    """
    phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    token = os.environ["WHATSAPP_TOKEN"]
    recipient = _normalize_number(os.environ["WHATSAPP_RECIPIENT_NUMBER"])

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
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

    print(f"[WHATSAPP] Sending to {recipient}...")
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    result = resp.json()

    if not resp.ok:
        print(f"[WHATSAPP] Failed for {recipient}: {result}")
        return result

    wamid = result.get("messages", [{}])[0].get("id", "unknown")
    print(f"[WHATSAPP] Delivered to {recipient} — wamid: {wamid}")
    return result
