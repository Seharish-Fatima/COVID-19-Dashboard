import pandas as pd

REGION_NAMES = {
    "AFRO": "Africa",
    "AMRO": "Americas",
    "EMRO": "Eastern Mediterranean",
    "EURO": "Europe",
    "SEARO": "South-East Asia",
    "WPRO": "Western Pacific",
    "OTHER": "Other",
}


def load(path):
    df = pd.read_csv(path)
    df["Date_reported"] = pd.to_datetime(df["Date_reported"])
    df["Country"] = df["Country"].fillna("Unattributed")
    df["WHO_region"] = df["WHO_region"].fillna("OTHER").map(REGION_NAMES)
    return df


def countries(df, min_cumulative=10000):
    latest = df[df["Date_reported"] == df["Date_reported"].max()]
    keep = latest[latest["Cumulative_cases"] >= min_cumulative]["Country"]
    return sorted(c for c in keep if c != "Unattributed")


def country_series(df, name):
    s = df[df["Country"] == name].sort_values("Date_reported").reset_index(drop=True)
    return s


def global_series(df):
    g = df.groupby("Date_reported", as_index=False)[["New_cases", "New_deaths"]].sum()
    g["Cumulative_cases"] = g["New_cases"].cumsum()
    g["Cumulative_deaths"] = g["New_deaths"].cumsum()
    return g


def headline_stats(df):
    last = df["Date_reported"].max()
    latest = df[df["Date_reported"] == last]
    return {
        "countries": int(df.loc[df["Country"] != "Unattributed", "Country"].nunique()),
        "weeks": int(df["Date_reported"].nunique()),
        "first": df["Date_reported"].min(),
        "last": last,
        "total_cases": int(latest["Cumulative_cases"].sum()),
        "total_deaths": int(latest["Cumulative_deaths"].sum()),
    }