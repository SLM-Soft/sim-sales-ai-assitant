import re
from typing import List

CODE_FENCE_RE = re.compile(r"^```[\s\S]*?```", re.MULTILINE)

def strip_code_fences(text: str) -> str:
    # Удаляем любые code fences, если агент засунул контент в них
    return CODE_FENCE_RE.sub(lambda m: m.group(0).strip("`").strip(), text).strip()

def normalize_markdown_sections(text: str, required_sections: List[str], *, skip_empty: bool = False) -> str:
    """
    1) Удаляем явные мусорные префейсы/подписи.
    2) Гарантируем наличие всех секций в нужном порядке.
    """
    if not text:
        text = ""

    # уберём случайные преамбулы агента
    cleaned = text.strip()
    cleaned = cleaned.replace("\r\n", "\n").strip()

    # иногда агент кладет в тройные кавычки/фенсы — снимем
    cleaned = strip_code_fences(cleaned)

    # приведем множ. пустых строк
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # проверка/добавление секций
    out_lines: List[str] = []
    lower = cleaned.lower()

    # для быстрого поиска заголовков — простая эвристика
    def has_section(title: str) -> bool:
        return title.lower() in lower

    # если ни одной секции не заметили
    if not any(has_section(t) for t in required_sections):
        if skip_empty:
            return cleaned
        out = []
        for i, title in enumerate(required_sections):
            if i == 0:
                out.append(f"{title}\n\n{cleaned or '—'}")
            else:
                out.append(f"{title}\n\n—")
        return "\n\n".join(out).strip()

    # Иначе — проходим по требуемым заголовкам в порядке и вытягиваем их фрагменты
    # Простой парсер: режем по заголовкам, если они есть; если нет — вставляем пустой.
    remaining = cleaned
    for idx, title in enumerate(required_sections):
        pattern = re.compile(rf"(?m)^\s*{re.escape(title)}\s*$")
        match = pattern.search(remaining)
        if not match:
            if skip_empty:
                continue
            out_lines.append(f"{title}\n\n—")
            continue

        start = match.end()
        # ищем следующий заголовок из списка
        end = len(remaining)
        for nxt in required_sections[idx + 1:]:
            m2 = re.search(rf"(?m)^\s*{re.escape(nxt)}\s*$", remaining[start:])
            if m2:
                end = start + m2.start()
                break

        body = remaining[start:end].strip()
        if not body:
            if skip_empty:
                continue
            body = "—"
        out_lines.append(f"{title}\n\n{body}")

    return "\n\n".join(out_lines).strip()
