import os
import requests


TRELLO_BASE_URL = "https://api.trello.com/1"


def _auth_params():
    return {
        "key": os.environ["TRELLO_API_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
    }


def get_board_lists(board_id: str) -> list[dict]:
    """Fetch all lists on a board."""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/lists"
    resp = requests.get(url, params=_auth_params(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_list_cards(list_id: str) -> list[dict]:
    """Fetch all cards in a list with relevant fields."""
    url = f"{TRELLO_BASE_URL}/lists/{list_id}/cards"
    params = {
        **_auth_params(),
        "fields": "name,desc,due,dueComplete,labels,shortUrl,dateLastActivity",
        "members": "true",
        "member_fields": "fullName",
        "checklists": "all",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_board_data(board_id: str, target_list_names: list[str]) -> dict:
    """
    Fetch cards from specified lists on a board.

    Args:
        board_id: Trello board ID.
        target_list_names: List names to include (case-insensitive match).

    Returns:
        Dict mapping list name -> list of card dicts.
    """
    all_lists = get_board_lists(board_id)
    target_lower = {name.lower() for name in target_list_names}

    board_data = {}
    for lst in all_lists:
        if lst["name"].lower() in target_lower:
            cards = get_list_cards(lst["id"])
            board_data[lst["name"]] = _simplify_cards(cards)

    return board_data


def _simplify_cards(cards: list[dict]) -> list[dict]:
    """Extract only the fields we need for analysis."""
    simplified = []
    for card in cards:
        checklist_summary = []
        for cl in card.get("checklists", []):
            total = len(cl.get("checkItems", []))
            done = sum(1 for item in cl.get("checkItems", []) if item["state"] == "complete")
            checklist_summary.append({"name": cl["name"], "done": done, "total": total})

        simplified.append({
            "name": card["name"],
            "description": card.get("desc", "")[:300],
            "due": card.get("due"),
            "due_complete": card.get("dueComplete", False),
            "labels": [l["name"] for l in card.get("labels", []) if l.get("name")],
            "members": [m["fullName"] for m in card.get("members", [])],
            "checklists": checklist_summary,
            "url": card.get("shortUrl", ""),
            "last_activity": card.get("dateLastActivity", ""),
        })
    return simplified
