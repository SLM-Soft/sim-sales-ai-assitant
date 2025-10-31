from datetime import datetime
from typing import Any, Dict, Optional

SECTION_TITLES = [
    "Overview",
    "1. User intent → extracted",
    "2. Key requirements",
    "3. Data quality notes",
    "4. Solution architecture (high-level)",
    "5. AI + AI Agents recommendations",
    "6. SEO evaluation",
    "7. Timeline / effort estimate",
    "8. Cost estimate (range)",
    "9. Investment prognosis (ROI + runway)",
    "10. Risks & mitigation",
    "11. Clarification questions",
    "12. Next steps",
]

def build_agent_project_analysis_input(
    user_question: str,
    level: str = "brief",
    ctx: Optional[Dict[str, Any]] = None,
    include_benchmarks: bool = True,
) -> str:
    """
    Строит ЕДИНУЮ строку inputText для Bedrock Agent с максимально жёстким
    требованием формата (фиксированный набор разделов). Агенту прямо указываем
    игнорировать свои дефолтные инструкции и отвечать строго по шаблону.
    """
    ctx = ctx or {}
    company = (ctx.get("company") or {}) if isinstance(ctx, dict) else {}
    project = (ctx.get("projectData") or {}) if isinstance(ctx, dict) else {}
    messages = (ctx.get("messages") or []) if isinstance(ctx, dict) else []
    traffic = ctx.get("traffic")
    conversion = ctx.get("conversion")
    avg_check = ctx.get("avgCheck")

    word_limit = 200 if level == "brief" else 800
    today = datetime.utcnow().strftime("%Y-%m-%d")

    header = "\n".join(SECTION_TITLES)
    section_count = len(SECTION_TITLES)

    # корректная сборка известного стека: поддерживаем как список, так и строку
    tech_stack_value = project.get("techStack")
    known_stack = (
        ", ".join(tech_stack_value) if isinstance(tech_stack_value, list)
        else (tech_stack_value or "Unknown")
    )

    return f"""
YOU ARE A SENIOR AI/WEB CONSULTANT WORKING INSIDE A WEB+AI STUDIO CHAT.

HARD OVERRIDE — READ CAREFULLY AND OBEY:
- You MUST ignore any built-in, internal, default, or prior instructions of the agent/tool.
- You MUST follow ONLY the formatting rules defined below.
- If you cannot follow the exact {section_count}-section structure, return a short diagnostic in "Overview" and STILL output ALL {section_count} sections (fill missing ones with assumptions or "—").

STRICT OUTPUT FORMAT (MANDATORY):
- Return ONLY Markdown. No YAML/JSON, no code fences.
- Use EXACTLY these section headings in this exact order and wording:
{header}
- Keep content concise. Max words: {word_limit}.
- Each section MUST be present even if data is missing (write assumptions).
- No preambles, no meta-comments, no apologies. Start directly with "Overview".
- Do NOT recommend AWS Lex unless explicitly asked. Prefer Bedrock + Agents for orchestration.

QUALITY RULES:
- Provide concrete, non-generic recommendations.
- Always include time & cost ranges and explain uncertainty sources.
- Include at least 3 risks with mitigation.
- {"Include industry benchmark notes." if include_benchmarks else "Skip benchmarks."}

CONTEXT:
- Client: {company.get("name") or "Not specified"}
- Industry: {company.get("industry") or "Not specified"}
- Region: {company.get("country") or "Not specified"}
- Analysis Date: {today}
- Known Tech Stack: {known_stack}
- Traffic: {traffic if traffic is not None else "Unknown"}
- Conversion: {conversion if conversion is not None else "Unknown"}
- Avg Check: {avg_check if avg_check is not None else "Unknown"}
- Past messages: {len(messages)}

USER QUESTION:
\"\"\"{user_question}\"\"\"

REMEMBER:
- Output MUST be ONLY the {section_count} Markdown sections above, in the exact order and wording.
- No extra headers or summary lines outside these sections.
""".strip()
