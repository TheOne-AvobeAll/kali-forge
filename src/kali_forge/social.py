from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from .policy import PolicyProfile, RiskLevel, get_policy

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)\d{3}[-.\s]?\d{4}")
_URL_RE = re.compile(r"https?://[^\s]+")
_TOKEN_RE = re.compile(r"(?:token|secret|key|password)\s*[:=]\s*[A-Za-z0-9_\-./:=]+", re.IGNORECASE)


def redact_content(text: str, rules: Iterable[str] | None = None) -> str:
    """Mask sensitive values such as emails, URLs, and tokens in social content."""
    redacted = str(text)
    for rule in rules or ("email", "phone", "url", "token"):
        if rule == "email":
            redacted = _EMAIL_RE.sub("[EMAIL_REDACTED]", redacted)
        elif rule == "phone":
            redacted = _PHONE_RE.sub("[PHONE_REDACTED]", redacted)
        elif rule == "url":
            redacted = _URL_RE.sub("[URL_REDACTED]", redacted)
        elif rule == "token":
            redacted = _TOKEN_RE.sub("[TOKEN_REDACTED]", redacted)
    return redacted


@dataclass(frozen=True)
class SocialRiskAssessment:
    """A structured risk assessment for an individual social signal."""

    source: str
    handle: str
    policy_name: str
    risk_level: RiskLevel
    score: int
    reasons: tuple[str, ...]
    redacted_content: str
    evidence_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "handle": self.handle,
            "policy_name": self.policy_name,
            "risk_level": self.risk_level.value,
            "score": self.score,
            "reasons": list(self.reasons),
            "redacted_content": self.redacted_content,
            "evidence_fingerprint": self.evidence_fingerprint,
        }


def evaluate_social_signal(
    content: str,
    source: str,
    policy: str | PolicyProfile = "brand-protection",
    handle: str = "unknown",
) -> SocialRiskAssessment:
    """Score a user's social signal according to an approved policy profile."""
    profile = get_policy(policy) if isinstance(policy, str) else policy
    source_name = str(source).strip().lower()
    if not source_name:
        raise ValueError("Source cannot be empty.")
    if source_name not in {item.lower() for item in profile.allowed_sources}:
        raise ValueError(
            f"Source '{source}' is not allowed by policy '{profile.name}'. Allowed sources: {', '.join(profile.allowed_sources)}"
        )

    normalized = str(content).strip()
    if not normalized:
        raise ValueError("Social signal content cannot be empty.")

    redacted = redact_content(normalized, profile.redaction_rules)
    lowered = redacted.lower()
    reasons: list[str] = []
    score = 0

    for keyword in profile.blocked_keywords:
        if keyword.lower() in lowered:
            score += 25
            reasons.append(f"blocked keyword: {keyword}")

    for keyword in profile.suspicious_keywords:
        if keyword.lower() in lowered:
            score += 10
            reasons.append(f"suspicious keyword: {keyword}")

    if _URL_RE.search(redacted):
        score += 8
        reasons.append("URL present")
    if _EMAIL_RE.search(redacted):
        score += 6
        reasons.append("email contact present")
    if _PHONE_RE.search(redacted):
        score += 6
        reasons.append("phone number present")
    if _TOKEN_RE.search(redacted):
        score += 12
        reasons.append("credential-like token present")

    if not reasons:
        reasons.append("no notable risk indicators found")

    if score >= 60:
        risk_level = RiskLevel.CRITICAL
    elif score >= 40:
        risk_level = RiskLevel.HIGH
    elif score >= 20:
        risk_level = RiskLevel.MEDIUM
    elif score >= 10:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.INFO

    evidence_fingerprint = hashlib.sha256(redacted.encode("utf-8")).hexdigest()[:32]
    return SocialRiskAssessment(
        source=source_name,
        handle=str(handle).strip() or "unknown",
        policy_name=profile.name,
        risk_level=risk_level,
        score=score,
        reasons=tuple(reasons),
        redacted_content=redacted,
        evidence_fingerprint=evidence_fingerprint,
    )


__all__ = ["SocialRiskAssessment", "evaluate_social_signal", "redact_content"]
