from datetime import timedelta


def analyze_gaps(candles, timeframe_minutes=60):
    gaps = []

    if len(candles) < 2:
        return gaps

    expected_delta = timedelta(minutes=timeframe_minutes)

    for i in range(1, len(candles)):
        previous = candles[i - 1]["time"]
        current = candles[i]["time"]

        delta = current - previous

        if delta > expected_delta:
            missing = int(delta.total_seconds() // expected_delta.total_seconds()) - 1

            gaps.append({
                "index": i,
                "previous": previous,
                "next": current,
                "duration_hours": delta.total_seconds() / 3600,
                "missing_candles": missing,
                "previous_weekday": previous.strftime("%A"),
                "next_weekday": current.strftime("%A"),
            })

    return gaps
