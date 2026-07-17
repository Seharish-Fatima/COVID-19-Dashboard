import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def smooth(values, window=4):
    return pd.Series(values).clip(lower=0).rolling(window, center=True, min_periods=1).mean().to_numpy()


def detect_waves(dates, new_cases, prominence_frac=0.08, min_distance=8):
    y = smooth(new_cases)
    if y.max() <= 0:
        return [], y
    peaks, props = find_peaks(y, prominence=prominence_frac * y.max(), distance=min_distance)
    waves = []
    for i, p in enumerate(peaks):
        left_bound = peaks[i - 1] if i > 0 else 0
        right_bound = peaks[i + 1] if i < len(peaks) - 1 else len(y) - 1
        left_seg = y[left_bound:p + 1]
        start = left_bound + int(np.flatnonzero(left_seg <= left_seg.min() + 1e-9)[-1]) if p > left_bound else left_bound
        end = p + int(np.argmin(y[p:right_bound + 1])) if right_bound > p else right_bound
        seg = slice(start, end + 1)
        waves.append({
            "n": i + 1,
            "start": dates[start],
            "peak": dates[p],
            "end": dates[end],
            "peak_weekly": float(np.asarray(new_cases, dtype=float).clip(0)[p]),
            "peak_smoothed": float(y[p]),
            "total_cases": float(np.asarray(new_cases, dtype=float).clip(0)[seg].sum()),
            "duration_weeks": int(end - start + 1),
        })
    return waves, y