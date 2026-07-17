import pandas as pd


def negative_corrections(df):
    neg = df[(df["New_cases"] < 0) | (df["New_deaths"] < 0)].copy()
    neg = neg[["Date_reported", "Country", "New_cases", "New_deaths"]]
    return neg.sort_values("New_cases").reset_index(drop=True)


def reporting_pulse(df):
    active = df[df["New_cases"] > 0].groupby("Date_reported")["Country"].nunique()
    return active.reset_index().rename(columns={"Country": "countries_reporting"})


def deaths_per_1k_cases(global_df, window=8):
    c = global_df["New_cases"].clip(lower=0).rolling(window, min_periods=4).sum()
    d = global_df["New_deaths"].clip(lower=0).rolling(window, min_periods=4).sum()
    out = global_df[["Date_reported"]].copy()
    out["deaths_per_1k"] = (d / c * 1000).where(c > 0)
    return out


def zero_streak_share(df):
    last_year = df[df["Date_reported"] >= df["Date_reported"].max() - pd.Timedelta(weeks=52)]
    by_country = last_year.groupby("Country")["New_cases"].sum()
    silent = (by_country == 0).sum()
    return int(silent), int(by_country.size)