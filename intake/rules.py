"""Early spike of the deterministic rules in Section 7.5 (R-4, R-6, R-7, R-8, R-9).

No model, no network: plain functions over values that extraction would produce.
"""
import re
import unicodedata

PARTICLES = {"de", "del", "la", "los", "las"}
BLOCKED = {"aprobado", "aprobada", "rechazado", "rechazada", "tasa", "approved", "rejected", "rate"}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _fold(text):
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def normalize_cedula(raw):
    """'8 - 888 - 4412' -> '8-888-4412'; None when unreadable."""
    if not raw:
        return None
    parts = re.findall(r"[0-9A-Za-z]+", raw.upper())
    return "-".join(parts) if len(parts) >= 3 else None


def file_document(cedula, open_cases, chat_cases):
    """R-4. open_cases: {case_id: cedula}. chat_cases: open case IDs for the sender's chat."""
    ced = normalize_cedula(cedula)
    suggestion = chat_cases[0] if len(chat_cases) == 1 else None
    if ced is None:
        return {"status": "held", "reason": "cedula unreadable", "suggestion": suggestion}
    matches = [cid for cid, c in open_cases.items() if normalize_cedula(c) == ced]
    if len(matches) == 1:
        return {"status": "filed", "case": matches[0]}
    reason = "cedula matches no open case" if not matches else "cedula matches several cases"
    return {"status": "held", "reason": reason, "suggestion": suggestion}


def compare_names(a, b):
    """R-6. Names never raise a conflict: 'match' or 'variant'."""
    if _fold(a).split() == _fold(b).split():
        return "match"
    return "variant"


def salary_conflicts(values, margin=0.10):
    """R-7. values: list of (document, 'gross'|'net', amount). Gross is never compared with net."""
    conflicts = []
    for kind in ("gross", "net"):
        group = [v for v in values if v[1] == kind]
        if len(group) < 2:
            continue
        low, high = min(v[2] for v in group), max(v[2] for v in group)
        if (high - low) / low > margin:
            conflicts.append({"kind": kind, "values": group})
    return conflicts


def css_missing_months(present, required):
    """R-8. Returns the required months that are absent, in calendar order. Nothing is estimated."""
    have = {_fold(m) for m in present}
    return [m for m in required if _fold(m) not in have]


def draft_problems(text, open_items, max_chars=600):
    """R-9. Empty list means the draft may be shown to the assistant."""
    problems = []
    folded = _fold(text)
    for item in open_items:
        if _fold(item) not in folded:
            problems.append(f"missing item: {item}")
    if re.search(r"b/\.|\$|\d+[.,]\d{2}", folded):
        problems.append("contains an amount")
    words = set(re.findall(r"[a-z]+", folded))
    for w in sorted(words & BLOCKED):
        problems.append(f"blocked word: {w}")
    if len(text) > max_chars:
        problems.append("too long")
    return problems
