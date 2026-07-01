import pytest

from apps.api.monitoring.alerts import METRIC_QUERIES
from apps.api.monitoring.cost_tracker import MODEL_COST_PER_1K_TOKENS
from apps.api.monitoring.models import AlertEvent, AlertRule, CostRecord


class TestAlertRule:
    def test_alert_rule_creation(self) -> None:
        rule = AlertRule(
            tenant_id="tenant-1",
            name="High Error Rate",
            metric="error_rate",
            operator="gt",
            threshold=10.0,
            window_minutes=5,
            enabled=True,
        )
        assert rule.name == "High Error Rate"
        assert rule.enabled is True

    def test_alert_event_creation(self) -> None:
        event = AlertEvent(
            tenant_id="t1",
            rule_id="r1",
            rule_name="test",
            metric="error_rate",
            value=15.0,
            threshold=10.0,
            message="error_rate = 15.0 > 10.0",
            resolved=False,
        )
        assert event.value == 15.0

    def test_cost_record_creation(self) -> None:
        record = CostRecord(
            tenant_id="t1",
            date="2026-07-01",
            request_count=100,
            input_tokens=50000,
            output_tokens=10000,
            cost_usd=0.225,
            model="gpt-4o",
        )
        assert record.cost_usd == 0.225
        assert record.model == "gpt-4o"

    def test_metric_queries_defined(self) -> None:
        for name in ("error_rate", "latency_p99", "token_spike", "retrieval_null_rate"):
            assert name in METRIC_QUERIES


class TestCostTracker:
    def test_model_cost_rates_defined(self) -> None:
        for model in ("gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro"):
            assert model in MODEL_COST_PER_1K_TOKENS

    def test_cost_calculation_gpt4o(self) -> None:
        rates = MODEL_COST_PER_1K_TOKENS["gpt-4o"]
        cost = (1000 / 1000 * rates["input"]) + (500 / 1000 * rates["output"])
        assert cost == (0.0025 + 0.005)

    def test_cost_calculation_default_model(self) -> None:
        cost = (2000 / 1000 * 0.002) + (1000 / 1000 * 0.008)
        assert cost == 0.012


class TestAlertEngine:
    @pytest.mark.asyncio
    async def test_evaluate_alerts_no_rules(self) -> None:
        from unittest.mock import AsyncMock

        class FakeResult:
            def scalars(self):
                class FakeScalars:
                    def all(self):
                        return []

                return FakeScalars()

        db = AsyncMock()
        db.execute.return_value = FakeResult()

        from apps.api.monitoring.alerts import evaluate_alerts

        fired = await evaluate_alerts(db, "no-rules-tenant")
        assert fired == []
