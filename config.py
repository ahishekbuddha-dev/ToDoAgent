import os

# Board ID from environment
TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID", "")

# ---------------------------------------------------------------
# TARGET LISTS — only cards from these lists will be fetched.
# Update these to match your Trello board's list names exactly.
# ---------------------------------------------------------------
TARGET_LIST_NAMES = [
    "To Do",
    "In Progress",
    "Blocked",
]
