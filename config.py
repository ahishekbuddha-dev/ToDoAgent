import os

# Board ID from environment
TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID", "")

# ---------------------------------------------------------------
# TARGET LISTS — only cards from these lists will be fetched.
# Update these to match your Trello board's list names exactly.
# ---------------------------------------------------------------
TARGET_LIST_NAMES = [
    "S2 - Warm Clients",
    "S3 - Qualified",
    "S4 - Assessment",
    "S5 - POC / Proposal prep",
    "S6 - POC Success/Proposal Eval",
    "S7 - Commericals Discussion",
    "S8 - Closure",

]
