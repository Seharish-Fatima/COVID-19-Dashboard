import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from engine import data, waves, dynamics, forensics

st.set_page_config(page_title="WAVEFORM", page_icon="📈", layout="wide")

INK = "#060B14"
PANEL = "#0C1420"
LINE = "#16222F"
CYAN = "#45E0E6"
CORAL = "#FF6B7A"
GOLD = "#E8C468"
MUTED = "#7A8CA0"
TEXT = "#D9E6F2"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
.stApp {{ background: {INK}; }}
html, body, [class*="css"] {{ font-family: 'JetBrains Mono', monospace; color: {TEXT}; }}
h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0.02em; }}
h1 {{ color: {CYAN} !important; }}
h2, h3 {{ color: {TEXT} !important; }}
section[data-testid="stSidebar"] {{ background: {PANEL}; border-right: 1px solid {LINE}; }}
div[data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid {LINE}; border-top: 2px solid {CYAN}; padding: 12px 16px; border-radius: 3px; }}
div[data-testid="stMetric"] label {{ color: {MUTED} !important; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; }}
div[data-testid="stMetricValue"] {{ color: {CYAN}; font-family: 'Space Grotesk', sans-serif; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 3px; color: {MUTED}; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.8rem; padding: 8px 20px; }}
.stTabs [aria-selected="true"] {{ background: {INK}; color: {CYAN} !important; border-color: {CYAN}; }}
.chart-note {{ background: {PANEL}; border: 1px solid {LINE}; border-left: 3px solid {GOLD}; border-radius: 3px; padding: 14px 18px; margin: 8px 0; }}
.chart-note .k {{ color: {MUTED}; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; }}
hr {{ border-color: {LINE}; }}
</style>
""", unsafe_allow_html=True)


def styled(fig, height=380):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(family="JetBrains Mono", color=TEXT, size=12),
        height=height,
        margin=dict(l=40, r=20, t=44, b=40),
        xaxis=dict(gridcolor=LINE, zerolinecolor=LINE),
        yaxis=dict(gridcolor=LINE, zerolinecolor=LINE),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


def note(label, text):
    st.markdown(f"<div class='chart-note'><span class='k'>{label}</span><br><span style='color:{TEXT}'>{text}</span></div>", unsafe_allow_html=True)


@st.cache_data(show_spinner="reading four years of weekly reports...")
def get_data():
    df = data.load("data/who_weekly.csv")
    return df, data.global_series(df), data.headline_stats(df), data.countries(df)


df, gdf, stats, country_list = get_data()

st.title("📈 Waveform")
st.markdown(f"<span style='color:{MUTED}'>the pandemic as a time series — WHO weekly data, {stats['countries']} countries, {stats['first'].date()} → {stats['last'].date()}. a closed dataset, read honestly.</span>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Reported cases", f"{stats['total_cases'] / 1e6:.0f}M")
c2.metric("Reported deaths", f"{stats['total_deaths'] / 1e6:.2f}M")
c3.metric("Weeks of data", f"{stats['weeks']}")
c4.metric("Countries", f"{stats['countries']}")

tab_waves, tab_growth, tab_cfr, tab_forensics = st.tabs(["Waves", "Growth", "Fatality", "Forensics"])

with tab_waves:
    st.markdown("### Every epidemic is a waveform")
    ctrl1, ctrl2 = st.columns([2, 1])
    default_ix = country_list.index("Pakistan") if "Pakistan" in country_list else 0
    sel = ctrl1.selectbox("Country", country_list, index=default_ix)
    sens = ctrl2.slider("Wave sensitivity", 2, 20, 8, help="Minimum peak prominence as % of the country's biggest wave. Lower = catches small early waves; higher = only the majors.")

    s = data.country_series(df, sel)
    dates = s["Date_reported"].tolist()
    raw = s["New_cases"].to_numpy()
    detected, smoothed = waves.detect_waves(dates, raw, prominence_frac=sens / 100)

    fig = go.Figure()
    palette = [CYAN, GOLD, CORAL, "#8FD694", "#C79BF2", "#F2A65A", "#6BA8FF", "#F27EB2"]
    for i, w in enumerate(detected):
        fig.add_vrect(x0=w["start"], x1=w["end"], fillcolor=palette[i % len(palette)], opacity=0.08, line_width=0)
    fig.add_trace(go.Bar(x=dates, y=np.clip(raw, 0, None), marker_color=LINE, name="weekly reported"))
    fig.add_trace(go.Scatter(x=dates, y=smoothed, mode="lines", line=dict(color=CYAN, width=2.5), name="4-week smoothed"))
    for i, w in enumerate(detected):
        fig.add_trace(go.Scatter(x=[w["peak"]], y=[w["peak_smoothed"]], mode="markers+text", text=[f"W{w['n']}"], textposition="top center", textfont=dict(color=palette[i % len(palette)]), marker=dict(color=palette[i % len(palette)], size=10, symbol="diamond"), showlegend=False))
    fig.update_layout(title=f"{sel} — {len(detected)} detected waves", barmode="overlay")
    st.plotly_chart(styled(fig, 420), width="stretch")

    if detected:
        wt = pd.DataFrame(detected)
        wt["peak"] = wt["peak"].dt.date
        wt["start"] = wt["start"].dt.date
        wt["end"] = wt["end"].dt.date
        wt["peak_weekly"] = wt["peak_weekly"].map(lambda v: f"{v:,.0f}")
        wt["total_cases"] = wt["total_cases"].map(lambda v: f"{v:,.0f}")
        st.dataframe(wt[["n", "start", "peak", "end", "duration_weeks", "peak_weekly", "total_cases"]], width="stretch", hide_index=True)

    note("why the slider exists", "Wave detection has no ground truth — it's a prominence threshold on a smoothed series. At 8% a country's early waves can vanish under an Omicron peak fifty times their size; at 2% reporting noise starts qualifying as waves. The honest move is showing the dial, not hiding the choice.")

with tab_growth:
    st.markdown("### How fast is fast")
    sel_multi = st.multiselect("Compare countries", country_list, default=[c for c in ["Pakistan", "India", "United States of America"] if c in country_list])
    fig = go.Figure()
    fig2 = go.Figure()
    readouts = []
    for i, name in enumerate(sel_multi):
        s = data.country_series(df, name)
        g = dynamics.growth_rate(s["New_cases"].to_numpy())
        dt = dynamics.doubling_time_weeks(s["New_cases"].to_numpy())
        color = [CYAN, GOLD, CORAL, "#8FD694", "#C79BF2", "#6BA8FF"][i % 6]
        fig.add_trace(go.Scatter(x=s["Date_reported"], y=g, mode="lines", name=name, line=dict(color=color, width=2)))
        fig2.add_trace(go.Scatter(x=s["Date_reported"], y=dt, mode="lines", name=name, line=dict(color=color, width=2)))
        fa = dynamics.fastest_ascent(s["Date_reported"].tolist(), s["New_cases"].to_numpy())
        if fa:
            readouts.append(f"{name}: fastest climb +{fa['growth_pct']:.0f}%/wk in {fa['date'].strftime('%b %Y')}")
    fig.add_hline(y=0, line_color=MUTED, line_width=1)
    fig.update_layout(title="Week-over-week growth of smoothed cases (%)")
    st.plotly_chart(styled(fig), width="stretch")
    fig2.update_layout(title="Doubling time during ascents (weeks — lower is scarier)", yaxis_range=[0, 12])
    st.plotly_chart(styled(fig2, 320), width="stretch")
    if readouts:
        note("fastest ascents", " · ".join(readouts) + ". Nearly every country's record climb lands in the Omicron era — the variant that made every previous growth curve look polite.")

with tab_cfr:
    st.markdown("### The falling case-fatality curve (and its lies)")
    cfr_g = dynamics.lagged_cfr(gdf["New_cases"].to_numpy(), gdf["New_deaths"].to_numpy())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=gdf["Date_reported"], y=cfr_g, mode="lines", line=dict(color=CORAL, width=2.5), name="global lagged CFR"))
    eras = [("2020-12-14", "Alpha"), ("2021-06-01", "Delta"), ("2021-12-01", "Omicron")]
    for d, label in eras:
        fig.add_vline(x=pd.Timestamp(d).timestamp() * 1000, line_dash="dot", line_color=MUTED)
        fig.add_annotation(x=pd.Timestamp(d), y=1.0, yref="paper", text=label, showarrow=False, font=dict(color=MUTED, size=11))
    fig.update_layout(title="Global CFR — 8-week deaths over 8-week cases, cases lagged 2 weeks (%)", yaxis_range=[0, 16])
    st.plotly_chart(styled(fig, 400), width="stretch")

    note("read this chart with suspicion", "The terrifying 2020 spike is not lethality — it's arithmetic on a world that couldn't test. Divide real deaths by a fraction of real cases and CFR inflates. The genuine story is the middle: from ~2% in the Delta era to under 1% through Omicron — immunity, vaccines, and milder variants pulling the ratio down. And the late-2023 uptick? That's testing dying, not people: the denominator collapsed first.")

    sel_cfr = st.multiselect("Country CFR", country_list, default=[c for c in ["Pakistan", "Germany", "Peru"] if c in country_list])
    fig = go.Figure()
    for i, name in enumerate(sel_cfr):
        s = data.country_series(df, name)
        cfr = dynamics.lagged_cfr(s["New_cases"].to_numpy(), s["New_deaths"].to_numpy())
        color = [CYAN, GOLD, CORAL, "#8FD694", "#C79BF2", "#6BA8FF"][i % 6]
        fig.add_trace(go.Scatter(x=s["Date_reported"], y=cfr, mode="lines", name=name, line=dict(color=color, width=2)))
    fig.update_layout(title="Country-level lagged CFR (%)", yaxis_range=[0, 16])
    st.plotly_chart(styled(fig, 340), width="stretch")

with tab_forensics:
    st.markdown("### The dataset is also a patient")
    pulse = forensics.reporting_pulse(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pulse["Date_reported"], y=pulse["countries_reporting"], mode="lines", fill="tozeroy", line=dict(color=CYAN, width=2), fillcolor="rgba(69,224,230,0.12)"))
    fig.update_layout(title="Countries reporting any new cases, per week")
    st.plotly_chart(styled(fig, 340), width="stretch")

    peak_rep = int(pulse["countries_reporting"].max())
    final_rep = int(pulse["countries_reporting"].iloc[-2])
    silent, total = forensics.zero_streak_share(df)
    m1, m2, m3 = st.columns(3)
    m1.metric("Peak countries reporting", peak_rep)
    m2.metric("Final full week", final_rep)
    m3.metric("Silent for the last year", f"{silent}/{total}")

    note("the surveillance flatline", f"At its peak, {peak_rep} countries filed weekly case counts. By the dataset's final full week: {final_rep}. {silent} countries reported literally zero cases for the entire last 52 weeks — not because COVID ended, but because counting did. Every 2023 number in this dataset is a shadow of an unmeasured thing.")

    st.markdown("### Negative case weeks — when countries un-count")
    neg = forensics.negative_corrections(df)
    labels = neg["Country"] + " " + neg["Date_reported"].dt.strftime("%b %Y")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=neg["New_cases"].where(neg["New_cases"] < 0, 0), marker_color=CORAL, name="cases corrected"))
    fig.add_trace(go.Bar(x=labels, y=neg["New_deaths"].where(neg["New_deaths"] < 0, 0), marker_color=GOLD, name="deaths corrected"))
    fig.update_layout(title="Bulk corrections: negative weekly counts", barmode="relative")
    st.plotly_chart(styled(fig, 320), width="stretch")

    show = neg.copy()
    show["Date_reported"] = show["Date_reported"].dt.date
    st.dataframe(show, width="stretch", hide_index=True)

    dpk = forensics.deaths_per_1k_cases(gdf)
    fig = go.Figure(go.Scatter(x=dpk["Date_reported"], y=dpk["deaths_per_1k"], mode="lines", line=dict(color=GOLD, width=2)))
    fig.update_layout(title="Reported deaths per 1,000 reported cases (global, 8-week window)")
    st.plotly_chart(styled(fig, 320), width="stretch")

    note("what a correction means", f"The Philippines deleted {abs(int(neg.iloc[0]['New_cases'])):,} cases in one week of {neg.iloc[0]['Date_reported'].strftime('%b %Y')} — a database cleanup surfacing as negative epidemiology. {len(neg)} such weeks exist. The engine clips negatives to zero for rates and smoothing, and reports them here instead of pretending time flows backward.")