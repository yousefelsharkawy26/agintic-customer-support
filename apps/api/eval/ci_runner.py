import json
import sys
from pathlib import Path
from typing import Any, cast

import structlog

from apps.api.core.interfaces import LLMConfig
from apps.api.eval.harness import EvalHarness, EvalResult
from apps.api.models.router import ModelRouter

logger = structlog.get_logger()

BASELINE_FILE = Path("data/eval_baseline.json")


def load_baseline() -> dict[str, Any]:
    if BASELINE_FILE.exists():
        return cast("dict[str, Any]", json.loads(BASELINE_FILE.read_text()))
    return {}


def save_baseline(results: list[EvalResult]) -> None:
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(
        json.dumps({r.question_id: {"passed": r.passed, **r.metrics} for r in results}, indent=2)
    )
    logger.info("baseline_saved", path=str(BASELINE_FILE))


def check_regression(
    results: list[EvalResult], baseline: dict[str, Any], threshold: float = 0.1
) -> bool:
    regressions = 0
    for r in results:
        if r.question_id in baseline:
            prev_passed = baseline[r.question_id]["passed"]
            curr_passed = r.passed
            if prev_passed and not curr_passed:
                regressions += 1
                logger.warning(
                    "regression_detected", question_id=r.question_id, question=r.question
                )

    current_rate = sum(1 for r in results if r.passed) / max(len(results), 1)
    prev_rate = sum(1 for qid, v in baseline.items() if v["passed"]) / max(len(baseline), 1)

    if prev_rate > 0 and (prev_rate - current_rate) > threshold:
        logger.error(
            "pass_rate_regression",
            previous=round(prev_rate, 3),
            current=round(current_rate, 3),
            threshold=threshold,
        )
        return False

    if regressions > 0:
        logger.warning("regressions_found", count=regressions)
        return False

    return True


async def run_eval_ci(update_baseline: bool = False) -> int:
    llm = ModelRouter().select("ci_eval")
    harness = EvalHarness()
    config = LLMConfig(max_tokens=512, temperature=0)

    logger.info("eval_ci_starting", questions=len(harness._questions))
    results = await harness.run_all(llm, config)
    summary = harness.summary(results)

    logger.info(
        "eval_ci_complete",
        total=summary["total"],
        passed=summary["passed"],
        pass_rate=summary["pass_rate"],
    )

    baseline = load_baseline()

    if not baseline:
        logger.info("no_baseline_found_creating", path=str(BASELINE_FILE))
        save_baseline(results)
        return 0

    if update_baseline:
        save_baseline(results)
        logger.info("baseline_updated")
        return 0

    passed = check_regression(results, baseline)

    if summary["pass_rate"] < 70.0:
        logger.error("pass_rate_below_threshold", rate=summary["pass_rate"])
        return 1

    if not passed:
        logger.error("regression_check_failed")
        return 1

    return 0


if __name__ == "__main__":
    import asyncio

    update = "--update-baseline" in sys.argv
    exit_code = asyncio.run(run_eval_ci(update_baseline=update))
    sys.exit(exit_code)
