import json
from openai import OpenAI


SYSTEM_PROMPT = """You are an expert B2B sales strategist. You receive structured data from a Trello sales pipeline board. Each card represents a deal/prospect at a specific pipeline stage.

Your job is to analyze every card deeply — read the description, comments, checklist items, labels, due dates, and last activity — and recommend specific, actionable next steps from a sales perspective.

Think like a seasoned sales leader:
- What stage is this deal in? Is it progressing or stalled?
- Are there overdue follow-ups or missed deadlines?
- What blockers exist and how can they be removed?
- What's the next concrete action to move this deal forward?
- Are there deals at risk that need immediate attention?

Pipeline stages for context:
- S2 (Warm Clients): Initial interest shown — action: qualify, schedule discovery call
- S3 (Qualified): Need confirmed — action: deep-dive, stakeholder mapping
- S4 (Assessment): Evaluating fit — action: technical demo, solution design
- S5 (POC / Proposal Prep): Building proof — action: deliver POC, draft proposal
- S6 (POC Success / Proposal Eval): Decision pending — action: follow up, handle objections
- S7 (Commercials Discussion): Pricing/terms — action: negotiate, get sign-off
- S8 (Closure): Final steps — action: contract, onboarding prep

OUTPUT FORMAT (strictly follow this — it will be sent as a WhatsApp message):

Daily Sales Action Plan - <date>

TO DO:

1. <Card Name>
   Stage: <stage>
   Action: <1-2 specific recommended actions>
   Why: <brief reason — overdue/stalled/high priority/next step needed>
   Link: <trello card url>

2. <Card Name>
   ...

(continue for all cards that need action today)

PRIORITY ALERTS:
- List any overdue or at-risk deals here with urgency

Rules:
- Use plain text only, NO markdown (no *, no #, no []() links). Just plain URLs.
- Keep each card's recommendation to 2-3 lines max.
- Order by urgency: overdue first, then due today, then stalled deals, then active deals needing next steps.
- Skip cards marked as due_complete: true unless they have pending checklist items.
- Be specific — don't say "follow up", say "send pricing proposal" or "schedule technical demo with CTO".
"""


def generate_todo_list(board_data: dict, today: str) -> str:
    """
    Send board data to OpenAI and get back a sales-focused daily action plan.

    Args:
        board_data: Dict mapping list name -> list of enriched card dicts.
        today: Today's date string (YYYY-MM-DD).

    Returns:
        The generated action plan as plain text.
    """
    client = OpenAI()

    user_message = (
        f"Today's date: {today}\n\n"
        f"Trello sales pipeline data:\n{json.dumps(board_data, indent=2, default=str)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        max_tokens=3000,
    )

    return response.choices[0].message.content.strip()
