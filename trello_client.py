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
    """Fetch all cards in a list with full detail."""
    url = f"{TRELLO_BASE_URL}/lists/{list_id}/cards"
    params = {
        **_auth_params(),
        "fields": "name,desc,due,dueComplete,labels,shortUrl,dateLastActivity",
        "members": "true",
        "member_fields": "fullName",
        "checklists": "all",
        "attachments": "true",
        "attachment_fields": "name,url",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_card_comments(card_id: str, limit: int = 10) -> list[dict]:
    """Fetch recent comments/actions on a card."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}/actions"
    params = {
        **_auth_params(),
        "filter": "commentCard",
        "limit": limit,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    actions = resp.json()
    return [
        {
            "author": a.get("memberCreator", {}).get("fullName", "Unknown"),
            "date": a.get("date", ""),
            "text": a.get("data", {}).get("text", ""),
        }
        for a in actions
    ]


def fetch_board_data(board_id: str, target_list_names: list[str]) -> dict:
    """
    Fetch cards from specified lists on a board with full context.

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
            board_data[lst["name"]] = _enrich_cards(cards, lst["name"])

    return board_data


def _enrich_cards(cards: list[dict], list_name: str) -> list[dict]:
    """Extract all relevant fields and fetch comments for each card."""
    enriched = []
    for card in cards:
        checklist_details = []
        for cl in card.get("checklists", []):
            items = []
            for item in cl.get("checkItems", []):
                items.append({"name": item["name"], "done": item["state"] == "complete"})
            checklist_details.append({"name": cl["name"], "items": items})

        comments = get_card_comments(card["id"])

        enriched.append({
            "name": card["name"],
            "stage": list_name,
            "description": card.get("desc", ""),
            "due": card.get("due"),
            "due_complete": card.get("dueComplete", False),
            "labels": [l["name"] for l in card.get("labels", []) if l.get("name")],
            "members": [m["fullName"] for m in card.get("members", [])],
            "checklists": checklist_details,
            "comments": comments,
            "attachments": [
                {"name": a.get("name", ""), "url": a.get("url", "")}
                for a in card.get("attachments", [])
            ],
            "url": card.get("shortUrl", ""),
            "last_activity": card.get("dateLastActivity", ""),
        })
    return enriched
