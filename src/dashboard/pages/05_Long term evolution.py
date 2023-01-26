import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

from datetime import date, timedelta
import time

# -----------------------------------------------------------------------------
# Importing Data
# -----------------------------------------------------------------------------

df_days = pd.read_pickle("../../src/dashboard/data/garmin_days.pkl")
df_weeks = pd.read_pickle("../../src/dashboard/data/garmin_weeks.pkl")
df_months = pd.read_pickle("../../src/dashboard/data/garmin_months.pkl")

# -----------------------------------------------------------------------------
# Transforming dataframes for the ease of streamlit components
# -----------------------------------------------------------------------------

# Convert duration columns to float because streamlit doesn't handle durations
cols = [
    "moderate_activity_time",
    "vigorous_activity_time",
    "intensity_time",
    "start_sleep_time",
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
    "avg_rr_sleep",
]
for col in cols:
    df_days[col] = df_days[col].apply(lambda x: x.total_seconds())
    df_weeks[col] = df_weeks[col].apply(lambda x: x.total_seconds())
    df_months[col] = df_months[col].apply(lambda x: x.total_seconds())

df_days = df_days.reset_index()
df_days = df_days.rename(columns={"day": "date"})

df_weeks = df_weeks.reset_index()
df_weeks = df_weeks.rename(columns={"day": "date"})

df_months = df_months.reset_index()
df_months = df_months.rename(columns={"day": "date"})
df_months["month_year"] = df_months["date"].dt.strftime("%Y-%m")


# -----------------------------------------------------------------------------
# HR evolution
# -----------------------------------------------------------------------------

base = alt.Chart(df_weeks).encode(alt.X("date:T", axis=alt.Axis(title=None)))
area = base.mark_area(opacity=0.3, color="#57A44C").encode(
    alt.Y("hr_max", axis=alt.Axis(title="hr", titleColor="#57A44C")), alt.Y2("hr_min")
)
line1 = base.mark_line(stroke="#5276A7", interpolate="monotone").encode(
    alt.Y(
        "inactive_hr_avg", axis=alt.Axis(title="inactive_hr_avg", titleColor="#5276A7")
    )
)

# alt.layer(area, line1).resolve_scale(y="independent")

st.altair_chart(area + line1, use_container_width=True)
