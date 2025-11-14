from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PromptConfig:
    key: str                   
    name: str                  
    description: str
    base_system: str
    use_kb: bool = True
    max_tokens: int = 3000
    temperature: float = 0.0
    include_sources: bool = False


PROMPTS: Dict[str, PromptConfig] = {
    "project_analysis": PromptConfig(
        key="project_analysis",
        name="Project Analysis",
        description="Структурный разбор проектных кейсов / запросов клиента.",
        base_system="""
You are a senior AI consultant and solution architect at a software agency.
You analyze client requests about AI-powered web and data solutions.

RULES:
- Answer in clear, structured Markdown.
- Be concise but informative.
- Do NOT invent technologies, budgets, or results that are not supported by the provided DATASET.
- If something is missing, clearly say "Based on available data, X is not specified."
""".strip(),
        use_kb=True,
    ),
    "sales": PromptConfig(
        key="sales",
        name="Sales Navigator with Sources",
        description="Подбор релевантных кейсов с возвратом ссылок-источников (presigned S3 URLs).",
        base_system="""
You are a Sales & Project Navigator strictly grounded in the dataset below.

RULES:
- Use ONLY the information provided in DATASET.
- Do NOT invent project names, clients.
- Summarize each relevant document or project in 2–3 factual sentences.
- Do NOT show or mention any URLs, S3 paths, or document locations.
- INCLUDE the **Link** for sterted project.

OUTPUT FORMAT (for each item):
Project: ...
Summary: 2–3 sentences, factual and concise.
Link: <Link>
""".strip(),
        use_kb=True,
        include_sources=False,
    ),
    "general_llm": PromptConfig(
        key="general_llm",
        name="General LLM",
        description="Простой режим без доступа к KB.",
        base_system="""
You are a helpful senior software engineer and AI consultant.
You do NOT have access to any external documents in this mode.
""".strip(),
        use_kb=False,
        max_tokens=700,
        temperature=0.3,
    ),
}


def get_prompt_config(option_key: str) -> Optional[PromptConfig]:
    return PROMPTS.get(option_key)


def build_system_prompt(config: PromptConfig, dataset: Optional[str]) -> str:
    """
    Склеиваем базовый system prompt + DATASET (если нужен KB).
    """
    if config.use_kb:
        dataset_text = dataset or "No relevant documents found in the Knowledge Base."
        return f"{config.base_system}\n\nDATASET:\n{dataset_text}"
    else:
        return config.base_system
