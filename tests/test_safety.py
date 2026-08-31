from bot.execution.risk_engine import (
    RiskConfig,
    calculate_position_size,
    check_account_limits,
)

cfg = RiskConfig(
    risk_percent=0.5,
    max_daily_loss_percent=2.0,
    max_drawdown_percent=10.0,
    min_lot=0.01,
    max_lot=5.0,
    lot_step=0.01,
)

print("=== HMB FOREX AI V302 SAFETY TEST ===")

# 1. Normal position sizing
r = calculate_position_size(
    balance=1000.0,
    entry=1.1000,
    stop_loss=1.0950,
    config=cfg,
)

assert r.allowed
assert r.position_size > 0
print("PASS: 0.5% risk position sizing")

# 2. Invalid SL
r = calculate_position_size(
    balance=1000.0,
    entry=1.1000,
    stop_loss=1.1000,
    config=cfg,
)

assert not r.allowed
print("PASS: Invalid stop-loss rejected")

# 3. Daily loss limit
allowed, reason = check_account_limits(
    equity=979.0,
    daily_start_equity=1000.0,
    peak_equity=1000.0,
    config=cfg,
)

assert not allowed
assert "daily loss" in reason.lower()
print("PASS: 2% daily loss protection")

# 4. Drawdown limit
# Daily loss is only 1%, but drawdown from peak is >10%.
allowed, reason = check_account_limits(
    equity=1009.0,
    daily_start_equity=1020.0,
    peak_equity=1130.0,
    config=cfg,
)

assert not allowed
assert "drawdown" in reason.lower()
print("PASS: 10% maximum drawdown protection")

# 5. Healthy account
allowed, reason = check_account_limits(
    equity=995.0,
    daily_start_equity=1000.0,
    peak_equity=1000.0,
    config=cfg,
)

assert allowed
print("PASS: Healthy account allowed")

print()
print("=== ALL SAFETY TESTS PASSED ===")
