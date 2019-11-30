class LoanAgent:
    """Poloniex loan refresher agent. Keep offers current (i.e at fair rate)
    by cancelling loans older than 10min, and creating new loan offers at fair
    rates (average of lowest three rates)."""
