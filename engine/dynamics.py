import numpy as np
import pandas as pd
from .waves import smooth


def growth_rate(new_cases, window=4):
    y = pd.Series(smooth(new_cases, window))
    base = max(100.0, 0.01 * float(y.max()))
    prev = y.shift(1)
    g = (y / prev - 1.0).where((prev > base) & (y > base))
    return (g * 100).to_numpy()


def doubling_time_weeks(new_cases, window=4):
    y = pd.Series(smooth(new_cases, window))
    base = max(100.0, 0.01 * float(y.max()))
    prev = y.shift(1)
    ratio = (y / prev).where((prev > base) & (y > prev * 1.001))
    return (np.log(2) / np.log(ratio)).to_numpy()


def fastest_ascent(dates, new_cases):
    g = growth_rate(new_cases)
    if np.all(np.isnan(g)):
        return None
    i = int(np.nanargmax(g))
    return {"date": dates[i], "growth_pct": float(g[i])}


def lagged_cfr(new_cases, new_deaths, lag_weeks=2, window=8):
    c = pd.Series(new_cases).clip(lower=0).rolling(window, min_periods=4).sum().shift(lag_weeks)
    d = pd.Series(new_deaths).clip(lower=0).rolling(window, min_periods=4).sum()
    cfr = (d / c).where(c > 1000) * 100
    return cfr.clip(0, 25).to_numpy()