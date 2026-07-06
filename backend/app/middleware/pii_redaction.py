import re


PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "url": r"\bhttps?://\S+\b",
}


def redact_pii(text: str) -> str:
    result = text
    for label, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f"[REDACTED_{label.upper()}]", result)
    return result
