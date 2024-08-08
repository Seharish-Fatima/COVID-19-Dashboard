import streamlit as st
import pandas as pd
import numpy as np
import requests
from plotly.offline import iplot
import plotly.graph_objs as go
import plotly.express as px
import os
import warnings
import pycountry

warnings.filterwarnings('ignore')
st.set_page_config(page_title="COVID 19 Cases", page_icon=":medical_symbol:", layout="wide")
st.title(":pill: COVID-19 DASHBOARD")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
os.chdir(r"./WHO-COVID-19-global-data.csv")
df = pd.read_csv("WHO-COVID-19-global-data.csv")
col1, col2 = st.columns((2))
df['Date_reported'] = pd.to_datetime(df['Date_reported'], infer_datetime_format=True)
print(df.info())
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date"))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date"))
df['Date_reported'] = pd.to_datetime(df['Date_reported'])
df = df[(df["Date_reported"] >= date1) & (df["Date_reported"] <= date2)].copy()

st.sidebar.header("Choose Your Filter: ")
continent = st.sidebar.multiselect("Pick Your Continent: ", df["WHO_region"].unique())
if not continent:
    df2 = df.copy()
else:
    df2 = df[df["WHO_region"].isin(continent)]
country = st.sidebar.multiselect("Pick Your Country: ", df2["Country"].unique())
if not country:
    df3 = df2.copy()
else:
    df3 = df2[df2["Country"].isin(country)]
# Possibilities
if not continent and not country:
    filtered_df = df
elif not continent:
    filtered_df = df[df["Country"].isin(country)]
elif not country:
    filtered_df = df[df["WHO_region"].isin(continent)]
else:
    filtered_df = df3[df3["WHO_region"].isin(continent) & df3["Country"].isin(country)]
category_df = filtered_df.groupby(by=["WHO_region"], as_index=False)["Cumulative_cases"].sum()

with col1:
    st.subheader("Global COVID-19 Cases")
fig = px.scatter_geo(data_frame=filtered_df,
                     locations="Country",
                     locationmode='country names',
                     color="Cumulative_cases",
                     color_continuous_scale='plasma',
                     hover_name="Country",
                     size="Cumulative_cases",
                     projection="natural earth")
st.plotly_chart(fig, use_container_width=True, height=200)

st.subheader("Continent Wise Cases")
fig = px.bar(category_df, x="WHO_region", y="Cumulative_cases", template="seaborn")
st.plotly_chart(fig, use_container_width=True, height=200)
st.subheader("Country Wise Cases")
fig = px.pie(filtered_df, values="Cumulative_cases", names="Country", hole=0.5)
fig.update_traces(text=filtered_df["Country"], textposition="outside")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Cumulative Deaths Vs New Deaths")
fig = px.line(filtered_df, x='Country', y=["Cumulative_deaths", "New_deaths"])
st.plotly_chart(fig, use_container_width=True)
st.subheader("Country Wise New Cases")
fig = px.bar(filtered_df, x="Country", y="New_cases", template="seaborn")
st.plotly_chart(fig, use_container_width=True, height=200)
st.subheader("Date Wise New Cases")
fig = px.bar(df, x="Date_reported", y="New_cases", template="seaborn")
st.plotly_chart(fig, use_container_width=True, height=200)
st.subheader("Date Wise Total Cases")
fig = px.bar(df, x="Date_reported", y="Cumulative_cases", template="seaborn")
st.plotly_chart(fig, use_container_width=True, height=200)
