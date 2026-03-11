import os
import time
import requests


WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"
MAX_MESSAGE_LENGTH = 4000
MESSAGE_GAP_SECONDS = 5


def _normalize_number(number: str) -> str:
    """Ensure number has + prefix and no spaces."""
    number = number.replace(" ", "")
    if not number.startswith("+"):
        number = f"+{number}"
    return number


def _split_message(message: str) -> list[str]:
    """
    Split a long message into multiple chunks at logical boundaries.
    Splits on '---' separators first, then on double newlines, then on
    single newlines. Each chunk stays under MAX_MESSAGE_LENGTH.
    """
    if len(message) <= MAX_MESSAGE_LENGTH:
        return [message]

    chunks = []
    current = ""

    # First try splitting on '---' separators (our TO DO item dividers)
    sections = message.split("\n---\n")

    for i, section in enumerate(sections):
        separator = "\n---\n" if i < len(sections) - 1 else ""
        candidate = section + separator

        if len(current) + len(candidate) <= MAX_MESSAGE_LENGTH:
            current += candidate
        else:
            # Current chunk is full — save it
            if current.strip():
                chunks.append(current.strip())
            # If this single section is still too long, split further
            if len(candidate) > MAX_MESSAGE_LENGTH:
                sub_parts = _split_on_newlines(candidate)
                chunks.extend(sub_parts)
                current = ""
            else:
                current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks


def _split_on_newlines(text: str) -> list[str]:
    """Split text on double newlines, then single newlines if still too long."""
    chunks = []
    current = ""

    # Try double newlines first (paragraph breaks)
    paragraphs = text.split("\n\n")

    for i, para in enumerate(paragraphs):
        separator = "\n\n" if i < len(paragraphs) - 1 else ""
        candidate = para + separator

        if len(current) + len(candidate) <= MAX_MESSAGE_LENGTH:
            current += candidate
        else:
            if current.strip():
                chunks.append(current.strip())
            # If a single paragraph is still too long, split on single newlines
            if len(candidate) > MAX_MESSAGE_LENGTH:
                lines = candidate.split("\n")
                current = ""
                for line in lines:
                    if len(current) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
                        current += line + "\n"
                    else:
                        if current.strip():
                            chunks.append(current.strip())
                        current = line + "\n"
            else:
                current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks


def _send_single_message(url: str, headers: dict, recipient: str, message: str) -> dict:
    """Send a single WhatsApp message."""
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    result = resp.json()

    if not resp.ok:
        print(f"[WHATSAPP] Failed for {recipient}: {result}")
        return result

    wamid = result.get("messages", [{}])[0].get("id", "unknown")
    print(f"[WHATSAPP] Delivered to {recipient} — wamid: {wamid}")
    return result


def send_whatsapp_message(message: str) -> list[dict]:
    """
    Send a message via WhatsApp Business Cloud API.
    If the message exceeds the limit, it is split into logical chunks
    and sent sequentially with a 5-second gap.

    Returns:
        List of API response dicts (one per chunk).
    """
    phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    token = os.environ["WHATSAPP_TOKEN"]
    recipient = _normalize_number(os.environ["WHATSAPP_RECIPIENT_NUMBER"])

    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    chunks = _split_message(message)
    total = len(chunks)
    print(f"[WHATSAPP] Message split into {total} part(s) for {recipient}")

    results = []
    for i, chunk in enumerate(chunks):
        part_label = f"[Part {i + 1}/{total}] " if total > 1 else ""
        print(f"[WHATSAPP] Sending {part_label}to {recipient} ({len(chunk)} chars)...")

        result = _send_single_message(url, headers, recipient, chunk)
        results.append(result)

        # Wait between messages to ensure order and avoid rate limits
        if i < total - 1:
            print(f"[WHATSAPP] Waiting {MESSAGE_GAP_SECONDS}s before next part...")
            time.sleep(MESSAGE_GAP_SECONDS)

    return results
