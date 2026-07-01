from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, MessageRole

logger = structlog.get_logger()


@dataclass
class EvalQuestion:
    id: str
    question: str
    expected_topics: list[str]
    min_response_length: int = 20


@dataclass
class EvalResult:
    question_id: str
    question: str
    response: str
    model: str
    passed: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


GOLDEN_QUESTIONS: list[EvalQuestion] = [
    EvalQuestion("q001", "What are your business hours?", ["hours", "availability"]),
    EvalQuestion("q002", "How do I reset my password?", ["password", "account", "security"]),
    EvalQuestion("q003", "What is the refund policy?", ["refund", "policy", "returns"]),
    EvalQuestion("q004", "How do I cancel my subscription?", ["subscription", "cancel", "billing"]),
    EvalQuestion("q005", "Do you offer a free trial?", ["trial", "pricing", "free"]),
    EvalQuestion("q006", "How do I upgrade my plan?", ["upgrade", "plan", "pricing"]),
    EvalQuestion("q007", "What payment methods do you accept?", ["payment", "methods", "billing"]),
    EvalQuestion("q008", "How do I contact support?", ["contact", "support", "help"]),
    EvalQuestion("q009", "Can I change my email address?", ["email", "account", "settings"]),
    EvalQuestion("q010", "Is my data secure?", ["security", "data", "privacy"]),
    EvalQuestion("q011", "How do I export my data?", ["data", "export", "account"]),
    EvalQuestion("q012", "Do you have a mobile app?", ["mobile", "app", "platform"]),
    EvalQuestion("q013", "How long does shipping take?", ["shipping", "delivery", "time"]),
    EvalQuestion("q014", "Can I get a discount?", ["discount", "pricing", "promotion"]),
    EvalQuestion("q015", "What happens after I cancel?", ["cancel", "subscription", "account"]),
    EvalQuestion("q016", "How do I delete my account?", ["delete", "account", "data"]),
    EvalQuestion("q017", "Do you offer enterprise plans?", ["enterprise", "pricing", "plans"]),
    EvalQuestion("q018", "How do I invite team members?", ["team", "invite", "collaboration"]),
    EvalQuestion("q019", "What integrations do you support?", ["integrations", "api", "tools"]),
    EvalQuestion("q020", "How do I report a bug?", ["bug", "report", "support"]),
]


class EvalHarness:
    def __init__(self, questions: list[EvalQuestion] | None = None) -> None:
        self._questions = questions or GOLDEN_QUESTIONS

    async def run_all(
        self, llm_provider: LLMProvider, config: LLMConfig | None = None
    ) -> list[EvalResult]:
        results: list[EvalResult] = []
        cfg = config or LLMConfig(max_tokens=512)
        for q in self._questions:
            result = await self._evaluate_one(q, llm_provider, cfg)
            results.append(result)
        return results

    async def _evaluate_one(
        self, question: EvalQuestion, llm_provider: LLMProvider, config: LLMConfig
    ) -> EvalResult:
        messages = [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content="You are a helpful customer support assistant.",
            ),
            LLMMessage(role=MessageRole.USER, content=question.question),
        ]
        try:
            response = await llm_provider.generate(messages, config)
            passed = len(response.content) >= question.min_response_length and any(
                t in response.content.lower() for t in question.expected_topics
            )
            metrics = {
                "response_length": len(response.content),
                "expected_topics": question.expected_topics,
                "topics_found": [
                    t for t in question.expected_topics if t in response.content.lower()
                ],
            }
            return EvalResult(
                question_id=question.id,
                question=question.question,
                response=response.content,
                model=response.model,
                passed=passed,
                metrics=metrics,
            )
        except Exception as e:
            logger.error("eval_error", question_id=question.id, error=str(e))
            return EvalResult(
                question_id=question.id,
                question=question.question,
                response="",
                model="error",
                passed=False,
                metrics={"error": str(e)},
            )

    def summary(self, results: list[EvalResult]) -> dict[str, Any]:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0.0,
        }
