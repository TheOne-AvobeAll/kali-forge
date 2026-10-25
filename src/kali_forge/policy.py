from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    """Risk severity used by the social security policy engine."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PolicyProfile:
    """A policy controlling what sources are allowed and how risk is interpreted."""

    name: str
    description: str
    allowed_sources: tuple[str, ...] = (
        "twitter",
        "x",
        "linkedin",
        "reddit",
        "instagram",
        "discord",
        "mastodon",
    )
    allowed_commands: tuple[str, ...] = (
        "python",
        "python3",
        "echo",
        "jq",
        "grep",
        "sed",
        "awk",
    )
    required_approval: bool = True
    max_retention_days: int = 30
    redaction_rules: tuple[str, ...] = ("email", "phone", "url", "token")
    suspicious_keywords: tuple[str, ...] = (
        "phishing",
        "impersonation",
        "scam",
        "credential",
        "free money",
        "urgent verification",
        "click here",
        "fake login",
        "malware",
        "account takeover",
        "brand impersonation",
    )
    blocked_keywords: tuple[str, ...] = (
        "urgent verification",
        "free crypto",
        "password reset now",
        "steal credentials",
        "giveaway scam",
    )
    risk_threshold: RiskLevel = RiskLevel.MEDIUM

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Policy name cannot be empty.")
        if not self.description.strip():
            raise ValueError("Policy description cannot be empty.")
        if self.max_retention_days <= 0:
            raise ValueError("max_retention_days must be greater than zero.")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "allowed_sources": list(self.allowed_sources),
            "allowed_commands": list(self.allowed_commands),
            "required_approval": self.required_approval,
            "max_retention_days": self.max_retention_days,
            "redaction_rules": list(self.redaction_rules),
            "suspicious_keywords": list(self.suspicious_keywords),
            "blocked_keywords": list(self.blocked_keywords),
            "risk_threshold": self.risk_threshold.value,
        }


BUILTIN_POLICIES: dict[str, PolicyProfile] = {
    "brand-protection": PolicyProfile(
        name="brand-protection",
        description="Protect a brand or organization from impersonation, scam content, and suspicious outreach.",
        allowed_sources=("twitter", "x", "linkedin", "instagram", "mastodon"),
        allowed_commands=("python", "python3", "echo", "jq", "grep", "sed", "awk"),
        required_approval=True,
        max_retention_days=14,
        risk_threshold=RiskLevel.MEDIUM,
    ),
    "incident-response": PolicyProfile(
        name="incident-response",
        description="Handle active abuse, impersonation, or phishing signals with higher scrutiny and evidence capture.",
        allowed_sources=("twitter", "x", "reddit", "discord", "mastodon"),
        allowed_commands=("python", "python3", "echo", "jq", "grep", "sed", "awk"),
        required_approval=True,
        max_retention_days=30,
        risk_threshold=RiskLevel.HIGH,
        suspicious_keywords=(
            "phishing",
            "impersonation",
            "scam",
            "credential",
            "urgent verification",
            "malware",
            "account takeover",
            "brand impersonation",
            "compromised account",
        ),
        blocked_keywords=(
            "urgent verification",
            "free crypto",
            "password reset now",
            "steal credentials",
            "malware distribution",
        ),
    ),
    "threat-intel": PolicyProfile(
        name="threat-intel",
        description="Collect and analyze suspicious claims and malicious narratives while applying stricter approval requirements.",
        allowed_sources=("twitter", "x", "reddit", "mastodon"),
        allowed_commands=("python", "python3", "echo", "jq", "grep", "sed", "awk"),
        required_approval=True,
        max_retention_days=45,
        risk_threshold=RiskLevel.LOW,
    ),
}


def list_policies() -> tuple[PolicyProfile, ...]:
    return tuple(BUILTIN_POLICIES.values())


def get_policy(name: str) -> PolicyProfile:
    profile = BUILTIN_POLICIES.get(name.strip())
    if profile is None:
        raise ValueError(f"Policy '{name}' is not available.")
    return profile


__all__ = ["RiskLevel", "PolicyProfile", "BUILTIN_POLICIES", "list_policies", "get_policy"]
