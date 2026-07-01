from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class GuardrailResult:
    passed: bool
    issues: list[str] = field(default_factory=list)
    sanitized_input: str | None = None


PII_PATTERNS: dict[str, str] = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
}

INJECTION_PATTERNS: list[str] = [
    r"(?i)\bignore\s+(all\s+)?(previous|above|below)\b",
    r"(?i)\bforget\b.*\binstructions\b",
    r"(?i)\byou\s+are\s+(not\s+)?(a|an)\s+(chatbot|ai|assistant|bOT)\b",
    r"(?i)\bnew\s+instructions?\b",
    r"(?i)\brewrite\s+(your|the)\s+(system\s+)?prompt\b",
]

CONTENT_SAFETY_PATTERNS: list[str] = [
    r"(?i)\b(?:hack|exploit|bypass|malware|ransomware)\b",
    r"(?i)\b(?:suicide|self-harm|self.harm)\b",
]


def check_pii(text: str) -> list[str]:
    return [name for name, pattern in PII_PATTERNS.items() if re.search(pattern, text)]


def check_injection(text: str) -> list[str]:
    return [
        f"possible_prompt_injection_{i}"
        for i, p in enumerate(INJECTION_PATTERNS)
        if re.search(p, text)
    ]


def check_content_safety(text: str) -> list[str]:
    return [
        f"unsafe_content_{i}" for i, p in enumerate(CONTENT_SAFETY_PATTERNS) if re.search(p, text)
    ]


def sanitize_pii(text: str) -> str:
    result = text
    for name, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f"[REDACTED_{name.upper()}]", result)
    return result


def run_input_guardrails(text: str) -> GuardrailResult:
    issues: list[str] = []
    issues.extend(f"pii:{p}" for p in check_pii(text))
    issues.extend(f"injection:{p}" for p in check_injection(text))
    issues.extend(f"safety:{p}" for p in check_content_safety(text))

    sanitized = sanitize_pii(text) if any("pii" in i for i in issues) else text
    return GuardrailResult(passed=len(issues) == 0, issues=issues, sanitized_input=sanitized)


def run_output_guardrails(text: str) -> GuardrailResult:
    issues: list[str] = []
    issues.extend(f"pii:{p}" for p in check_pii(text))
    issues.extend(f"safety:{p}" for p in check_content_safety(text))
    return GuardrailResult(passed=len(issues) == 0, issues=issues)
