import sys
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from config import TRELLO_BOARD_ID, TARGET_LIST_NAMES
from trello_client import fetch_board_data
from analyzer import generate_todo_list
from whatsapp import send_whatsapp_message


IST = timezone(timedelta(hours=5, minutes=30))


def run():
    today = datetime.now(IST).strftime("%Y-%m-%d")
    print(f"[{today}] Fetching Trello board data...")

    if not TRELLO_BOARD_ID:
        print("ERROR: TRELLO_BOARD_ID is not set.")
        sys.exit(1)

    board_data = fetch_board_data(TRELLO_BOARD_ID, TARGET_LIST_NAMES)

    total_cards = sum(len(cards) for cards in board_data.values())
    print(f"Fetched {total_cards} cards from {len(board_data)} lists.")

    if total_cards == 0:
        message = f"Good morning! Your Trello board has no actionable items in {', '.join(TARGET_LIST_NAMES)}. Enjoy your day!"
    else:
        print("Generating to-do list with OpenAI...")
        message = generate_todo_list(board_data, today)

    print("Sending WhatsApp message...")
    result = send_whatsapp_message(message)
    print(f"WhatsApp message sent. Response: {result}")

    # Also print the message for GitHub Actions logs
    print("\n--- Generated To-Do List ---")
    print(message)


if __name__ == "__main__":
    run()
