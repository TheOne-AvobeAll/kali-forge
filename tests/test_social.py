from __future__ import annotations

import pytest

from kali_forge.policy import get_policy, list_policies
from kali_forge.social import evaluate_social_signal, redact_content


def test_list_policies_exposes_security_profiles() -> None:
    policies = list_policies()
    assert {entry.name for entry in policies} >= {"brand-protection", "incident-response", "threat-intel"}
    assert get_policy("brand-protection").name == "brand-protection"


def test_evaluate_social_signal_redacts_sensitive_values() -> None:
    assessment = evaluate_social_signal(
        "Urgent verification required at https://example.com/login token=abc123 user@example.com",
        "twitter",
        "brand-protection",
        "@suspicious",
    )
    assert assessment.score >= 20
    assert "[EMAIL_REDACTED]" in assessment.redacted_content
    assert "[URL_REDACTED]" in assessment.redacted_content
    assert "[TOKEN_REDACTED]" in assessment.redacted_content


def test_evaluate_social_signal_rejects_unapproved_sources() -> None:
    with pytest.raises(ValueError):
        evaluate_social_signal("free crypto giveaway", "facebook", "brand-protection", "@bad")


def test_redact_content_handles_phone_numbers() -> None:
    text = "Call 555-123-4567 now to verify your account."
    redacted = redact_content(text)
    assert "[PHONE_REDACTED]" in redacted
    assert "555-123-4567" not in redacted
