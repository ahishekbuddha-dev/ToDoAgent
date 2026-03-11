import json
from openai import OpenAI


SYSTEM_PROMPT = """You are a productivity assistant. You receive structured data from a Trello board and produce a clear, actionable daily to-do list.

Rules:
- Prioritize by: overdue items first, then due today, then items with high-priority labels, then by recent activity.
- Group tasks by their Trello list (e.g. "In Progress", "To Do").
- For each task include: task name, why it's prioritized, due date if any, checklist progress if any.
- Keep it concise and scannable — this will be sent as a WhatsApp message.
- Use plain text formatting (no markdown). Use numbered lists and line breaks.
- End with a short motivational line.
- If there are no actionable items, say so clearly.
"""


def generate_todo_list(board_data: dict, today: str) -> str:
    """
    Send board data to OpenAI and get back a prioritized daily to-do list.

    Args:
        board_data: Dict mapping list name -> list of simplified card dicts.
        today: Today's date string (YYYY-MM-DD).

    Returns:
        The generated to-do list as plain text.
    """
    client = OpenAI()

    user_message = (
        f"Today's date: {today}\n\n"
        f"Trello board data:\n{json.dumps(board_data, indent=2, default=str)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        max_tokens=1500,
    )

    return response.choices[0].message.content.strip()
