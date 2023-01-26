import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

import datetime
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
]
for col in cols:
    df_days[col] = df_days[col].apply(lambda x: x.total_seconds() / 60)
    df_weeks[col] = df_weeks[col].apply(lambda x: x.total_seconds() / 60)
    df_months[col] = df_months[col].apply(lambda x: x.total_seconds() / 60)

cols = [
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
]
for col in cols:
    df_days[col] = df_days[col].apply(lambda x: x.total_seconds() / 3600)
    df_weeks[col] = df_weeks[col].apply(lambda x: x.total_seconds() / 3600)
    df_months[col] = df_months[col].apply(lambda x: x.total_seconds() / 3600)

df_days = df_days.reset_index()
df_days = df_days.rename(columns={"day": "date"})

df_weeks = df_weeks.reset_index()
df_weeks = df_weeks.rename(columns={"day": "date"})
df_weeks = df_weeks[df_weeks["days_resampled"] >= 3]

df_months = df_months.reset_index()
df_months = df_months.rename(columns={"day": "date"})
df_months["month_year"] = df_months["date"].dt.strftime("%Y-%m")
df_months = df_months[df_months["days_resampled"] >= 10]

# -----------------------------------------------------------------------------
# Defining plotting functions
# -----------------------------------------------------------------------------


def create_bar_chart_with_goal(
    df,
    bar_color,
    lines_color,
    y,
    mean_value,
    goal_value,
    goal_above=True,
):
    max_value = df[y].max()
    # base = alt.Chart(df).encode(alt.X("date:T", axis=alt.Axis(title=None)))
    base = alt.Chart(df)
    bar_chart = base.mark_bar(
        color=bar_color,
        interpolate="linear",
        size=8,
        opacity=0.7,
        strokeCap="round",
    ).encode(
        alt.X(
            "date",
            axis=alt.Axis(
                title=None,
            ),
        ),
        alt.Y(
            y,
            axis=alt.Axis(title=None),
            scale=alt.Scale(
                domain=[0, max_value],
                nice=False,
            ),
        ),
        opacity=alt.condition(
            alt.datum[y] >= goal_value if goal_above else alt.datum[y] <= goal_value,
            alt.value(0.8),
            alt.value(0.5),
        ),
    )

    # Add horizontal line for mean value
    mean_value_line = (
        alt.Chart(pd.DataFrame({"value": [mean_value]}))
        .mark_rule(color=lines_color, strokeDash=[4, 4], opacity=0.3)
        .encode(y="value", size=alt.value(2))
    )

    # Add horizontal line for the goal
    given_value_line = (
        alt.Chart(pd.DataFrame({"value": [goal_value]}))
        .mark_rule(color=lines_color, opacity=0.3)
        .encode(y="value", size=alt.value(2))
    )

    chart = alt.layer(
        bar_chart + mean_value_line + given_value_line,
        data=df,
    )

    st.altair_chart(chart, use_container_width=True)


def create_line_chart_with_goal(
    df, bar_color, lines_color, y, mean_value, goal_value, min_y=0
):
    max_y = df[y].max() * 1.10
    # base = alt.Chart(df).encode(alt.X("date:T", axis=alt.Axis(title=None)))
    base = alt.Chart(df)
    bar_chart = base.mark_line(
        color=bar_color,
        # stroke="#FFC0CB",
        interpolate="linear",
        size=3,
        opacity=0.7,
    ).encode(
        alt.X(
            "date",
            axis=alt.Axis(
                title=None,
            ),
        ),
        alt.Y(
            y,
            axis=alt.Axis(title=None),
            scale=alt.Scale(
                domain=[min_y, max_y],
                nice=False,
            ),
        ),
    )

    # Add horizontal line for mean value
    mean_value_line = (
        alt.Chart(pd.DataFrame({"value": [mean_value]}))
        .mark_rule(color=lines_color, strokeDash=[4, 4], opacity=0.3)
        .encode(y="value", size=alt.value(2))
    )

    # Add horizontal line for the goal
    given_value_line = (
        alt.Chart(pd.DataFrame({"value": [goal_value]}))
        .mark_rule(color=lines_color, opacity=0.3)
        .encode(y="value", size=alt.value(2))
    )

    chart = alt.layer(
        bar_chart + mean_value_line + given_value_line,
        data=df,
    )

    st.altair_chart(chart, use_container_width=True)


# -----------------------------------------------------------------------------
# Setting up page Config
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Past performance & Goals",
    page_icon=":dart:",
    layout="wide",
    menu_items={
        "Get help": "https://www.linkedin.com/in/christophe-level",
        "About": "# This is a personal project. Visit my website for other projects: https://crish1eev1.github.io/",
    },
)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------

st.markdown("## Past performances & Future Goals")

# -----------------------------------------------------------------------------
# Defining Goals widgets
# -----------------------------------------------------------------------------

# Goal section title
st.markdown("### Goals")

# Create sliders in columns
col1, col2, col3, col4, col5 = st.columns(5, gap="large")

# Goal coefficient
with col1:
    goal_coef = st.slider(
        label="Goal multiplier",
        min_value=-1.0,
        max_value=3.0,
        value=0.25,
        step=0.05,
        help="Goal = [Last year mean] + [Goal multiplier] x [Standard Deviation]",
    )

with col2:
    reference_year = st.selectbox(
        label="Year of reference",
        options=[2022, 2021, 2020],
        help="...",
    )

# Filtering tables needed for goal setup
reference_mask = (df_months["date"] <= f"{reference_year}-12-31") & (
    df_months["date"] >= f"{reference_year}-01-01"
)
df_months_reference = df_months[reference_mask]

mask_2023 = (df_months["date"] >= "2023-01-01") & (df_months["date"] <= "2023-12-31")
df_months_2023 = df_months[mask_2023]

# Moderate Activity Goals
steps_mean = df_months_reference["steps"].mean()
steps_goal = steps_mean + (goal_coef) * df_months["steps"].std()
calories_mean = df_months_reference["calories"].mean()
calories_goal = calories_mean + (goal_coef) * df_months["calories"].std()
moderate_activity_time_mean = df_months_reference["moderate_activity_time"].mean()
moderate_activity_time_goal = (
    moderate_activity_time_mean
    + (goal_coef) * df_months["moderate_activity_time"].std()
)


# Vigorous Activity Goals
vigorous_activity_time_mean = df_months_reference["vigorous_activity_time"].mean()
vigorous_activity_time_goal = (
    vigorous_activity_time_mean
    + (goal_coef) * df_months["vigorous_activity_time"].std()
)


running_activities_mean = df_months_reference["running_activities"].mean()
running_activities_goal = (
    running_activities_mean + (goal_coef) * df_months["running_activities"].std()
)


running_distance_mean = df_months_reference["running_distance"].mean()
running_distance_goal = (
    running_distance_mean + (goal_coef) * df_months["running_distance"].std()
)


# Resting Goals
resting_hr_mean = df_months_reference["resting_hr"].mean()
resting_hr_goal = resting_hr_mean - (goal_coef) * df_months["resting_hr"].std()

stress_avg_mean = df_months_reference["stress_avg"].mean()
stress_avg_goal = stress_avg_mean - (goal_coef) * df_months["stress_avg"].std()

bb_min_mean = df_months_reference["bb_min"].mean()
bb_min_goal = bb_min_mean + (goal_coef) * df_months["bb_min"].std()


# Sleeping Goals
bb_charged_mean = df_months_reference["bb_charged"].mean()
bb_charged_goal = bb_charged_mean + (goal_coef) * df_months["bb_charged"].std()

bb_max_mean = df_months_reference["bb_max"].mean()
bb_max_goal = bb_max_mean + (goal_coef) * df_months["bb_max"].std()

start_sleep_time_mean = df_months_reference["start_sleep_time"].mean()
start_sleep_time_goal = (
    start_sleep_time_mean - (goal_coef) * df_months["start_sleep_time"].std()
)


# Goals
total_sleep_mean = df_months_reference["total_sleep"].mean()
total_sleep_goal = total_sleep_mean + (goal_coef) * df_months["total_sleep"].std()

deep_sleep_mean = df_months_reference["deep_sleep"].mean()
deep_sleep_goal = deep_sleep_mean + (goal_coef) * df_months["deep_sleep"].std()

rem_sleep_mean = df_months_reference["rem_sleep"].mean()
rem_sleep_goal = rem_sleep_mean + (goal_coef) * df_months["rem_sleep"].std()


# Goals
awake_mean = df_months_reference["awake"].mean()
awake_goal = awake_mean - (goal_coef) * df_months["awake"].std()

avg_rr_sleep_mean = df_months_reference["avg_rr_sleep"].mean()
avg_rr_sleep_goal = avg_rr_sleep_mean + (goal_coef) * df_months["avg_rr_sleep"].std()


# -----------------------------------------------------------------------------
# Moderate activity metrics
# -----------------------------------------------------------------------------

# Set title
st.markdown("### Moderate Activity metrics")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.write("Daily steps average")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#FFA0A0",
        lines_color="#FF6961",
        y="steps",
        mean_value=steps_mean,
        goal_value=steps_goal,
    )
    st.metric(
        label="Daily steps average in 2023 (vs goal)",
        value=int(df_months_2023["steps"].mean()),
        delta=int(df_months_2023["steps"].mean() - steps_goal),
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Daily calories average")
    create_line_chart_with_goal(
        df=df_months,
        bar_color="#FFA0A0",
        lines_color="#FF6961",
        y="calories",
        mean_value=calories_mean,
        goal_value=calories_goal,
        min_y=df_months["calories"].min() * 0.9,
    )
    st.metric(
        label="Daily calories average in 2023 (vs goal)",
        value=int(df_months_2023["calories"].mean()),
        delta=int(df_months_2023["calories"].mean() - calories_goal),
        help="test",
        label_visibility="visible",
    )

with col3:
    st.write("Daily moderate activity average (in minutes)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#FFA0A0",
        lines_color="#FF6961",
        y="moderate_activity_time",
        mean_value=moderate_activity_time_mean,
        goal_value=moderate_activity_time_goal,
    )
    st.metric(
        label="Daily moderate activity average in 2023 (vs goal)",
        value=int(df_months_2023["moderate_activity_time"].mean()),
        delta=int(
            df_months_2023["moderate_activity_time"].mean()
            - moderate_activity_time_goal
        ),
        help="test",
        label_visibility="visible",
    )

# -----------------------------------------------------------------------------
# Vigorous Activity metrics   vigorous_activity_time, running_activities, running_distance
# -----------------------------------------------------------------------------

# Set title
st.markdown("### Vigorous Activity metrics")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")


with col1:
    st.write("Daily vigorous activity average (in min)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#FF5151",
        lines_color="#FF6961",
        y="vigorous_activity_time",
        mean_value=vigorous_activity_time_mean,
        goal_value=vigorous_activity_time_goal,
    )
    st.metric(
        label="Daily vigorous activity time average in 2023 (vs goal)",
        value=int(df_months_2023["vigorous_activity_time"].mean()),
        delta=int(
            df_months_2023["vigorous_activity_time"].mean()
            - vigorous_activity_time_goal
        ),
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Monthly running sessions")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#FF5151",
        lines_color="#FF6961",
        y="running_activities",
        mean_value=running_activities_mean,
        goal_value=running_activities_goal,
    )
    st.metric(
        label="Monthly running sessions average in 2023 (vs goal)",
        value=int(df_months_2023["running_activities"].mean()),
        delta=int(
            df_months_2023["running_activities"].mean() - running_activities_goal
        ),
        help="test",
        label_visibility="visible",
    )

with col3:
    st.write("Monthly running distance (in km)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#FF5151",
        lines_color="#FF6961",
        y="running_distance",
        mean_value=running_distance_mean,
        goal_value=running_distance_goal,
    )
    st.metric(
        label="Monthly running distance average 2023 (vs goal)",
        value=int(df_months_2023["running_distance"].mean()),
        delta=int(df_months_2023["running_distance"].mean() - running_distance_goal),
        help="test",
        label_visibility="visible",
    )


# -----------------------------------------------------------------------------
# Resting metrics  (resting_hr, stress_avg, bb_min)
# -----------------------------------------------------------------------------

# Set title
st.markdown("### Resting metrics")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")


with col1:
    st.write("Daily resting heart rate average")
    create_line_chart_with_goal(
        df=df_months,
        bar_color="#87CEFA",
        lines_color="#0077BE",
        y="resting_hr",
        mean_value=resting_hr_mean,
        goal_value=resting_hr_goal,
        min_y=df_months["resting_hr"].min() * 0.9,
    )
    st.metric(
        label="Daily resting heart rate in 2023 (vs goal)",
        value=int(df_months_2023["resting_hr"].mean()),
        delta=int(df_months_2023["resting_hr"].mean() - resting_hr_goal),
        delta_color="inverse",
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Daily stress average")
    create_line_chart_with_goal(
        df=df_months,
        bar_color="#87CEFA",
        lines_color="#0077BE",
        y="stress_avg",
        mean_value=stress_avg_mean,
        goal_value=stress_avg_goal,
        min_y=df_months["stress_avg"].min() * 0.9,
    )
    st.metric(
        label="Daily stress average in 2023 (vs goal)",
        value=int(df_months_2023["stress_avg"].mean()),
        delta=int(df_months_2023["stress_avg"].mean() - stress_avg_goal),
        delta_color="inverse",
        help="test",
        label_visibility="visible",
    )

with col3:
    st.write("Daily minimum body battery average")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#87CEFA",
        lines_color="#0077BE",
        y="bb_min",
        mean_value=bb_min_mean,
        goal_value=bb_min_goal,
    )
    st.metric(
        label="Daily minimum body battery average in 2023 (vs goal)",
        value=int(df_months_2023["bb_min"].mean()),
        delta=int(df_months_2023["bb_min"].mean() - bb_min_goal),
        help="test",
        label_visibility="visible",
    )


# -----------------------------------------------------------------------------
# Sleeping metrics (bb_charged, bb_max, start_sleep_time)
# -----------------------------------------------------------------------------

# Set title
st.markdown("### Sleeping metrics")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")


with col1:
    st.write("Daily charged body battery average")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="bb_charged",
        mean_value=bb_charged_mean,
        goal_value=bb_charged_goal,
    )
    st.metric(
        label="Daily charged body battery average in 2023 (vs goal)",
        value=int(df_months_2023["bb_charged"].mean()),
        delta=int(df_months_2023["bb_charged"].mean() - bb_charged_goal),
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Daily max body battery average")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="bb_max",
        mean_value=bb_max_mean,
        goal_value=bb_max_goal,
    )
    st.metric(
        label="Daily max body battery average in 2023 (vs goal)",
        value=int(df_months_2023["bb_max"].mean()),
        delta=int(df_months_2023["bb_max"].mean() - bb_max_goal),
        help="test",
        label_visibility="visible",
    )

with col3:
    st.write("Daily starting sleep time average (in minutes vs midnight)")
    create_line_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="start_sleep_time",
        mean_value=start_sleep_time_mean,
        goal_value=start_sleep_time_goal,
        min_y=df_months["start_sleep_time"].min() * 0.9,
    )
    st.metric(
        label="Daily starting sleep time in 2023 (vs goal)",
        value=int(df_months_2023["start_sleep_time"].mean()),
        delta=int(df_months_2023["start_sleep_time"].mean() - start_sleep_time_goal),
        delta_color="inverse",
        help="test",
        label_visibility="visible",
    )


# -----------------------------------------------------------------------------
# Sleeping metrics (total_sleep, deep_sleep, rem_sleep awake)
# -----------------------------------------------------------------------------

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")


with col1:
    st.write("Daily total sleep average (in hours)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="total_sleep",
        mean_value=total_sleep_mean,
        goal_value=total_sleep_goal,
    )
    st.metric(
        label="Daily total sleep in 2023 (vs goal)",
        value=df_months_2023["total_sleep"].mean().round(1),
        delta=(df_months_2023["total_sleep"].mean() - total_sleep_goal).round(1),
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Daily deep_sleep average (in hours)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="deep_sleep",
        mean_value=deep_sleep_mean,
        goal_value=deep_sleep_goal,
    )
    st.metric(
        label="Daily deep sleep in 2023 (vs goal)",
        value=df_months_2023["deep_sleep"].mean().round(1),
        delta=(df_months_2023["deep_sleep"].mean() - deep_sleep_goal).round(1),
        help="test",
        label_visibility="visible",
    )

with col3:
    st.write("Daily rem_sleep average (in hours)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="rem_sleep",
        mean_value=rem_sleep_mean,
        goal_value=rem_sleep_goal,
    )
    st.metric(
        label="Daily rem sleep in 2023 (vs goal)",
        value=df_months_2023["rem_sleep"].mean().round(1),
        delta=(df_months_2023["rem_sleep"].mean() - rem_sleep_goal).round(1),
        help="test",
        label_visibility="visible",
    )


# -----------------------------------------------------------------------------
# Sleeping metrics (awake, avg_rr_sleep)
# -----------------------------------------------------------------------------

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")


with col1:
    st.write("Daily night awake time average (in hours)")
    create_bar_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="awake",
        mean_value=awake_mean,
        goal_value=awake_goal,
        goal_above=False,
    )
    st.metric(
        label="Daily night awake time 2023 (vs goal)",
        value=df_months_2023["awake"].mean().round(2),
        delta=(df_months_2023["awake"].mean() - awake_goal).round(2),
        delta_color="inverse",
        help="test",
        label_visibility="visible",
    )

with col2:
    st.write("Daily average nightly respiration rate")
    create_line_chart_with_goal(
        df=df_months,
        bar_color="#6495ED",
        lines_color="#0077BE",
        y="avg_rr_sleep",
        mean_value=avg_rr_sleep_mean,
        goal_value=avg_rr_sleep_goal,
        min_y=df_months["avg_rr_sleep"].min() * 0.9,
    )
    st.metric(
        label="Daily average nightly respiration rate 2023 (vs goal)",
        value=df_months_2023["avg_rr_sleep"].mean().round(1),
        delta=(df_months_2023["avg_rr_sleep"].mean() - avg_rr_sleep_goal).round(1),
        help="test",
        delta_color="inverse",
        label_visibility="visible",
    )

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

df_days
df_weeks
df_months

print(df_days.info())
print(df_months.info())


# -----------------------------------------------------------------------------
# Being active (3): steps, calories, moderate_activity_time
# Doing sport (3): vigorous_activity_time, running_activities, running_distance
# Resting (3): resting_hr, stress, bb_min
# Sleeping (8): bb_charged, bb_max, start_sleep_time, total_sleep, deep_sleep, rem_sleep awake, awake, avg_rr_sleep,
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
""" 
alt.base.mark_bar() method:

    size: sets the width of the bars.
    opacity: sets the transparency of the bars.
    color: sets the color of the bars.
    stroke: sets the color of the bar's stroke.
    strokeWidth: sets the width of the bar's stroke.
    tooltip: sets the fields to include in the tooltip when hovering over a bar.
    interpolate: sets the interpolation method for the bar.
    barPadding: sets the padding between the bars.
    barSize: sets the size of the bars.
    barThickness: sets the thickness of the bars.
    cornerRadiusTopLeft: sets the corner radius of the top left corner of the bars.
    cornerRadiusTopRight: sets the corner radius of the top right corner of the bars.
    cornerRadiusBottomLeft: sets the corner radius of the bottom left corner of the bars.
    cornerRadiusBottomRight: sets the corner radius of the bottom right corner of the bars.
    align: sets the alignment of the bars.
    baseline: sets the baseline position of the bars.
    sort: sets the sort order of the bars.
    x2: sets the x2 position of the bars.
    y2: sets the y2 position of the bars.
"""
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# TO DO:
# - Change goals to make it based on 2022 year
# - Show 2023 bars in another color
# - Try to color graphs to show what is good/bad
# - Add "help" explenations to metrics (currently "test")
# -----------------------------------------------------------------------------
