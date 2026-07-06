from app.middleware.pii_redaction import redact_pii


def test_email_redaction():
    text = "Contact me at john.doe@example.com for details."
    result = redact_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "john.doe@example.com" not in result


def test_phone_redaction():
    text = "Call me at (555) 123-4567."
    result = redact_pii(text)
    assert "[REDACTED_PHONE]" in result


def test_multiple_pii():
    text = "Email: a@b.com, Phone: 555-000-1111"
    result = redact_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_PHONE]" in result
