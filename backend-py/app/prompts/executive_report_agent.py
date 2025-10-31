from datetime import datetime
from typing import Any, Dict, Optional

EXEC_SECTION_TITLES = [
    "1. TL;DR (one paragraph)",
    "2. Objectives → extracted",
    "3. Current KPIs & insights",
    "4. Key risks",
    "5. Recommendations (top 3)",
    "6. Timeline & owners",
    "7. Metrics to watch",
    "8. Open questions",
    "9. Next steps",
]

def build_agent_executive_report_input(
    user_question: str,
    level: str = "brief",
    ctx: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Промпт для краткого исполнительского отчёта (executive one‑pager):
    цели, текущие метрики, риски, рекомендации и следующие шаги.
    """
    ctx = ctx or {}
    company = (ctx.get("company") or {}) if isinstance(ctx, dict) else {}
    today = datetime.utcnow().strftime("%Y-%m-%d")

    header = "\n".join(EXEC_SECTION_TITLES)
    word_limit = 160 if level == "brief" else 500

    return f"""
YOU ARE A SENIOR PRODUCT/AI CONSULTANT PREPARING AN EXECUTIVE ONE-PAGER.

RULES:
- Use ONLY the headings below. Markdown only. No preambles.
- Be business-friendly and concise; make decisions easy.

STRICT OUTPUT FORMAT (MANDATORY):
- EXACT headings in this order:
{header}
- Max words: {word_limit}.

CONTEXT:
- Client: {company.get('name') or 'Not specified'}
- Date: {today}

CLIENT QUESTION:
\"\"\"{user_question}\"\"\"

REMEMBER:
- Recommendations must be concrete and prioritized.
- Timeline must include owners (roles) at minimum.
""".strip()


