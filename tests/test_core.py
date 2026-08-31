import unittest
from datetime import datetime, timezone

from bot.execution.account import Account
from bot.execution.costs import ExecutionCosts, calculate_execution
from bot.execution.risk_engine import RiskConfig, calculate_position_size
from bot.core.data_validator import validate_candles


class CoreTests(unittest.TestCase):
    def test_position_size_respects_risk(self):
        cfg = RiskConfig(risk_percent=0.5, pip_size=0.0001, pip_value_per_lot=10.0)
        result = calculate_position_size(1000.0, 1.1000, 1.0990, cfg)
        self.assertTrue(result.allowed)
        self.assertAlmostEqual(result.position_size, 0.05)

    def test_execution_costs(self):
        costs = ExecutionCosts(spread_pips=1.0, slippage_pips=0.2, commission_per_lot=7.0)
        buy = calculate_execution("BUY", 1.1000, 0.05, costs)
        self.assertGreater(buy.executed_price, 1.1000)
        self.assertAlmostEqual(buy.commission, 0.35)

    def test_daily_reset(self):
        from bot.execution.trade_engine import TradeEngine
        engine = TradeEngine(Account(1000.0))
        engine.start_new_day(datetime(2025, 1, 2, tzinfo=timezone.utc))
        engine.account.balance = 990.0
        engine.start_new_day(datetime(2025, 1, 3, tzinfo=timezone.utc))
        self.assertAlmostEqual(engine.daily_start_equity, 990.0)

    def test_data_validator_accepts_weekly_forex_gaps(self):
        candles = []
        for hour in (20, 21):
            candles.append({
                "time": datetime(2025, 1, 3, hour, tzinfo=timezone.utc),
                "open": 1.1, "high": 1.101, "low": 1.099,
                "close": 1.1, "volume": 1,
            })
        candles.append({
            "time": datetime(2025, 1, 6, 0, tzinfo=timezone.utc),
            "open": 1.1, "high": 1.101, "low": 1.099,
            "close": 1.1, "volume": 1,
        })
        report = validate_candles(candles)
        self.assertTrue(report.valid)
        self.assertEqual(report.unexpected_missing_intervals, 0)


if __name__ == "__main__":
    unittest.main()
