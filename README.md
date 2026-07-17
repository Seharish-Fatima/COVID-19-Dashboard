# Waveform 📈

### Live: [waveform.streamlit.app](https://waveform.streamlit.app/)

Everyone remembers the pandemic in vibes — "the Delta summer," "that Omicron winter," "when they stopped counting." But 211 weeks of WHO surveillance data for 234 countries are sitting right there, so this app reads the whole thing as what it actually is: a time series. Waves you can detect, growth you can measure, fatality curves you can interrogate — and a dataset that slowly dies on camera in the final act.

712 million reported cases. 6.2 million reported deaths. Both numbers are undercounts, and the app is honest about why.

## What it actually does (no cap)

Four tabs, each one a different way of reading the same signal:

- **Waves** — pick a country, and a peak-detection algorithm (smoothed series + prominence threshold) finds its epidemic waves, shades them, and tabulates each one: start, peak, duration, total cases. **Pakistan shows 6 waves. India shows 3 giant ones. South Africa shows its textbook 5.** And there's a sensitivity slider, because wave detection has no ground truth — at the default threshold the US shows 4 waves, but its 2020 waves are hiding under an Omicron peak fifty times their height. Drag the slider down and watch them surface. **The dial is the lesson.**
- **Growth** — week-over-week growth rates and doubling times, comparable across countries. Nearly every country's fastest-ever climb lands in the Omicron era: **Pakistan's record ascent was +129% per week in January 2022.** The variant that made every previous growth curve look polite.
- **Fatality** — the global case-fatality ratio, lagged and windowed properly (8-week sums, cases shifted 2 weeks, because people don't die the week they test positive). The curve falls from **~2% in the Delta era to under 1% through Omicron** — immunity, vaccines, milder variants. The scary 2020 spike? Not lethality — arithmetic on a world that couldn't test. The chart keeps it and the caption calls it out.
- **Forensics** — my favorite tab: the dataset itself as the patient. At peak, **220 countries reported weekly cases. In the final full week: 3.** Twenty-five countries reported literally zero cases for the entire last year — counting ended before COVID did. Plus the bulk corrections: **the Philippines deleted 65,079 cases in a single week** of August 2023, one of 28 negative-count weeks where countries quietly un-counted.

Every chart ends with a callout that says what it means — because a time series without interpretation is just a squiggle.

## Project structure

```
waveform/
├── app.py                  # the actual app (Streamlit UI)
├── engine/
│   ├── data.py             # loading, cleaning, global aggregation
│   ├── waves.py            # smoothing + peak detection + wave boundaries
│   ├── dynamics.py         # growth rates, doubling time, lagged CFR
│   └── forensics.py        # corrections, reporting pulse, silence detection
├── data/who_weekly.csv     # the dataset, bundled — app works instantly, no upload
└── requirements.txt
```

`engine/` does the math. `app.py` only renders. The engine doesn't know Streamlit exists — same separation as my other apps, because it keeps working when the UI changes. Every module was tested against the real data before the UI touched it.

## A real note on the source data (there's always something)

- **28 weeks in this dataset have negative new cases or deaths.** Countries filing bulk corrections — database cleanups surfacing as reverse epidemiology. The engine clips negatives to zero for smoothing and rates, and reports every one of them in Forensics instead of pretending time flows backward.
- **The data is weekly, not daily.** WHO switched cadence — every gap between consecutive reports is exactly 7 days. All windows, lags, and doubling times in the app are in weeks, and labeled as weeks.
- **1,260 rows have no country name and 5,040 no WHO region.** Mapped to "Unattributed"/"Other" — they're kept in global totals (those cases happened to someone) but excluded from country pickers.
- **Early-2020 rates are small-number theater.** Growth on a base of 200 cases produces +600%/week numbers that mean nothing. Every rate in the app has a base threshold — 1% of a country's own peak — before it's allowed to render.
- **The final year is a mirage.** Case counts after mid-2022 track testing policy, not infection. The app doesn't correct for this (nobody honestly can) — it dedicates a tab to demonstrating it instead.
- Cutoff is **January 2024** because that's where this WHO snapshot ends. A fixed historical dataset, analyzed as exactly that.

## Running this yourself

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dataset is bundled — it just works. Or use the live deployment above, zero setup.

## Dataset

WHO's [COVID-19 global weekly data](https://data.who.int/dashboards/covid19/data) — official country-reported surveillance, Jan 2020 through Jan 2024. Reported numbers only; true infections and deaths were higher everywhere. The app analyzes what was counted, and spends a whole tab on what wasn't.
