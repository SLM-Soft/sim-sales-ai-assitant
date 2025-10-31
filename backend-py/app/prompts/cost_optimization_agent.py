from datetime import datetime
from typing import Any, Dict, Optional

COST_SECTION_TITLES = [
    "Overview",
    "1. Current spend drivers → extracted",
    "2. Quick wins (next 2 weeks)",
    "3. Architecture & infra recommendations",
    "4. App/runtime optimizations",
    "5. Process & tooling (FinOps/SDLC)",
    "6. Expected savings (range, by item)",
    "7. Risks & trade-offs",
    "8. Implementation plan (phased)",
    "9. Metrics to monitor",
    "10. Open questions",
    "11. Next steps",
]

def build_agent_cost_optimization_input(
    user_question: str,
    level: str = "brief",
    ctx: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Жёсткий промпт для консультации по оптимизации затрат (Web/Cloud/AI).
    Даёт конкретные действия с оценкой экономии и планом внедрения.
    """
    ctx = ctx or {}
    company = (ctx.get("company") or {}) if isinstance(ctx, dict) else {}
    stack = (ctx.get("projectData", {}) or {}).get("techStack") if isinstance(ctx, dict) else None
    today = datetime.utcnow().strftime("%Y-%m-%d")

    header = "\n".join(COST_SECTION_TITLES)
    word_limit = 180 if level == "brief" else 700

    return f"""
YOU ARE A SENIOR WEB/AI COST OPTIMIZATION CONSULTANT.

HARD RULES:
- Follow ONLY the format below. No preambles. Markdown only.
- Be concrete and actionable; avoid generic advice.
- Include ranges and name trade-offs when proposing changes.

STRICT OUTPUT FORMAT (MANDATORY):
- Use EXACTLY these headings in this exact order:
{header}
- Keep content concise. Max words: {word_limit}.
- If data is missing, make reasonable assumptions and label them.

CONTEXT:
- Client: {company.get('name') or 'Not specified'}
- Known Tech Stack: {', '.join(stack or []) if isinstance(stack, list) else 'Unknown'}
- Date: {today}

CLIENT QUESTION:
\"\"\"{user_question}\"\"\"

REMEMBER:
- Quantify expected monthly savings by item where possible.
- Separate quick wins from longer initiatives.
- Highlight risks (e.g., performance, availability, team bandwidth).
""".strip()


