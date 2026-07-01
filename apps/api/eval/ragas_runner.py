from typing import Any

import structlog
from datasets import Dataset

from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, MessageRole
from apps.api.eval.dataset import GOLDEN_QA
from apps.api.eval.harness import EvalResult

logger = structlog.get_logger()


class RAGEvalRunner:
    def __init__(self, questions: list[dict[str, Any]] | None = None) -> None:
        self._questions: list[dict[str, Any]] = questions or GOLDEN_QA

    def _q(self, item: dict[str, Any]) -> str:
        return str(item["question"])

    def _a(self, item: dict[str, Any]) -> str:
        return str(item["answer"])

    async def run(self, llm_provider: LLMProvider) -> list[EvalResult]:
        results: list[EvalResult] = []
        cfg = LLMConfig(max_tokens=512, temperature=0)

        for item in self._questions:
            messages = [
                LLMMessage(
                    role=MessageRole.SYSTEM, content="Answer concisely based on the context."
                ),
                LLMMessage(role=MessageRole.USER, content=self._q(item)),
            ]
            try:
                response = await llm_provider.generate(messages, cfg)
                passed = len(response.content) > 20
                results.append(
                    EvalResult(
                        question_id=self._q(item)[:30],
                        question=self._q(item),
                        response=response.content,
                        model=response.model,
                        passed=passed,
                        metrics={
                            "response_length": len(response.content),
                            "exact_answer": self._a(item),
                        },
                    )
                )
            except Exception as e:
                logger.error("eval_error", question=self._q(item), error=str(e))
                results.append(
                    EvalResult(
                        question_id=self._q(item)[:30],
                        question=self._q(item),
                        response="",
                        model="error",
                        passed=False,
                        metrics={"error": str(e)},
                    )
                )
        return results

    def to_hf_dataset(self, results: list[EvalResult]) -> Dataset:
        data = {
            "question": [r.question for r in results],
            "answer": [r.response for r in results],
            "contexts": [[""] for _ in results],
            "ground_truth": [self._get_answer(r.question) for r in results],
        }
        return Dataset.from_dict(data)

    def _get_answer(self, question: str) -> str:
        for item in self._questions:
            if self._q(item) == question:
                return self._a(item)
        return ""

    def summary(self, results: list[EvalResult]) -> dict[str, Any]:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        avg_length = sum(len(r.response) for r in results) / total if total else 0
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0.0,
            "avg_response_length": round(avg_length, 1),
        }
