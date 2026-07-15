import time


def calculate_latency_ms(start_time_seconds: float) -> float:
    """Calculates processing latency in milliseconds since the start time."""
    return round((time.time() - start_time_seconds) * 1000, 2)
