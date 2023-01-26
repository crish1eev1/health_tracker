# -----------------------------------------------------------------------------
# command: streamlit run your_script.py
#
# I want to be able to see week-1 versus week-2 versus average
# I want to be able to see current week versus objectives
# Activities: hr_max ? ; steps ; distance ; calories ; moderate_activity_time ; vigorous_activity_time ; intensity_time ; running_distance; sweat_loss
# Well-being: stress ; resting_hr ; (try to take 2 days minimum in order to account for "rest days" ?)

# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Transforming dataframes for the ease of streamlit components
# -----------------------------------------------------------------------------

# Create a dictionary to map day of the week integers to strings
day_of_week = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# Extract day of the week from index and map it to string
df_days["day_of_week"] = df_days.index.dayofweek.map(day_of_week)

# Convert duration columns to float because streamlit doesn't handle durations
cols = ["moderate_activity_time", "vigorous_activity_time", "intensity_time"]
for col in cols:
    df_days[col] = df_days[col].apply(lambda x: x.total_seconds())

# Select a subset dataframe to work with for the Activity Metrics
df_days_active = df_days[
    [
        "steps",
        "distance",
        "calories",
        "day_of_week",
        "hr_max",
        "moderate_activity_time",
        "vigorous_activity_time",
        "intensity_time",
        "running_activities",
        "running_calories",
        "running_distance",
        "sweat_loss",
    ]
]

# -----------------------------------------------------------------------------
# Setting up page Config
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Weekly Goals",
    page_icon=":dart:",
    layout="wide",
    menu_items={
        "Get help": "https://www.linkedin.com/in/christophe-level",
        "About": "# This is a personal project. Visit my website for other projects: https://crish1eev1.github.io/",
    },
)

# -----------------------------------------------------------------------------
# Utils functions
# -----------------------------------------------------------------------------

# Find closest past monday
def find_closest_monday():
    now = date.today()
    closest_monday = now - timedelta(days=now.weekday())
    if closest_monday > now:
        closest_monday -= timedelta(days=7)
    return closest_monday


# Select the weekly data based on starting monday
def select_weekly_df(week_start_date):
    week_end_date = week_start_date + pd.DateOffset(days=6)
    week_end_date = pd.to_datetime(week_end_date).date()
    df_week = df_days_active.loc[week_start_date:week_end_date]
    df_week = df_week.reindex()
    return df_week


# -----------------------------------------------------------------------------
# Plot functions
# -----------------------------------------------------------------------------

# Function to plot a weekly bar-graph with option horizontal line
def bar_plot_weekly_df(
    df,
    y_col_name,
    x_col_name,
    x_label="day_of_week",
    show_x_label=True,
    y_label="quantity",
    show_y_label=True,
    show_h_line=False,
    h_line_value=None,
    line_color="red",
    bar_color="blue",
):
    if week_start_date.weekday() != 0:
        st.warning("Monday is the only valid choice. Please select a Monday.")
    else:
        # Create the chart
        chart = alt.Chart(df)
        if show_h_line and h_line_value is not None:
            line = (
                alt.Chart(pd.DataFrame({"y": [h_line_value]}))
                .mark_rule(
                    color=line_color, strokeWidth=2, opacity=0.5, strokeDash=[4, 4]
                )
                .encode(y="y")
            )
        chart = chart.mark_bar(color=bar_color).encode(
            x=alt.X(
                f"{x_col_name}:N",
                sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                axis=alt.Axis(title=x_label if show_x_label else None),
            ),
            y=alt.Y(
                f"{y_col_name}:Q",
                axis=alt.Axis(title=y_label if show_y_label else None),
            ),
        )
        # Display the chart in Streamlit
        if show_h_line and h_line_value is not None:
            st.altair_chart(chart + line, use_container_width=True)
        else:
            st.altair_chart(chart, use_container_width=True)


# -----------------------------------------------------------------------------
# Header elements (page title & main weekly filter)
# -----------------------------------------------------------------------------

# Page title
st.markdown("# Weekly Goals :dart:")

# Week main filter
closest_monday = find_closest_monday()

week_start_date = st.date_input(
    "Week's starting Monday :point_down:",
    value=closest_monday,
    key="date",
)
week_start_date = pd.to_datetime(week_start_date).date()

# Weekly dataframe to work with
df_week = select_weekly_df(week_start_date)


# -----------------------------------------------------------------------------
# Activity metrics elements (section title, objectives filters and plots elements)
# -----------------------------------------------------------------------------

# Section title
st.markdown("## Activity")
st.markdown("### Activity goals")


# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")

sliders = {
    "Steps goal": {
        "col": col1,
        "min_value": 0,
        "max_value": 20000,
        "value": 8000,
        "step": 500,
    },
    "Distance goal": {
        "col": col2,
        "min_value": 0,
        "max_value": 20,
        "value": 8,
        "step": 1,
    },
    "Calories goal": {
        "col": col3,
        "min_value": 0,
        "max_value": 4000,
        "value": 2000,
        "step": 100,
    },
    "HR goal": {
        "col": col1,
        "min_value": 0,
        "max_value": 220,
        "value": 160,
        "step": 10,
    },
    "Moderate activity time goal": {
        "col": col2,
        "min_value": 0,
        "max_value": 3000,
        "value": 500,
        "step": 100,
    },
    "Vigorous activity time goal": {
        "col": col3,
        "min_value": 0,
        "max_value": 3000,
        "value": 500,
        "step": 100,
    },
    "Intensity time goal": {
        "col": col1,
        "min_value": 0,
        "max_value": 3000,
        "value": 500,
        "step": 100,
    },
    "Running activities": {
        "col": col2,
        "min_value": 0.0,
        "max_value": 1.0,
        "value": 0.25,
        "step": 0.05,
    },
    "Running distance": {
        "col": col3,
        "min_value": 0.0,
        "max_value": 5.0,
        "value": 1.40,
        "step": 0.1,
    },
}

for key, value in sliders.items():
    value["goal"] = value["col"].slider(
        key,
        min_value=value["min_value"],
        max_value=value["max_value"],
        value=value["value"],
        step=value["step"],
    )

# Storing the output
step_goal = sliders["Steps goal"]["goal"]
distance_goal = sliders["Distance goal"]["goal"]
calories_goal = sliders["Calories goal"]["goal"]
hr_goal = sliders["HR goal"]["goal"]
moderate_activity_goal = sliders["Moderate activity time goal"]["goal"]
vigorous_activity_goal = sliders["Vigorous activity time goal"]["goal"]
intensity_time_goal = sliders["Intensity time goal"]["goal"]
running_activities_goal = sliders["Running activities"]["goal"]
running_distance_goal = sliders["Running distance"]["goal"]

st.markdown("### Activity graphs")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")

# Bar graphs
plots = {
    "Steps": {
        "col": col1,
        "y_col_name": "steps",
        "x_col_name": "day_of_week",
        "goal": step_goal,
    },
    "Distance (km)": {
        "col": col2,
        "y_col_name": "distance",
        "x_col_name": "day_of_week",
        "goal": distance_goal,
    },
    "Calories": {
        "col": col3,
        "y_col_name": "calories",
        "x_col_name": "day_of_week",
        "goal": calories_goal,
    },
    "HR max": {
        "col": col1,
        "y_col_name": "hr_max",
        "x_col_name": "day_of_week",
        "goal": hr_goal,
    },
    "Moderate Activity Time": {
        "col": col2,
        "y_col_name": "moderate_activity_time",
        "x_col_name": "day_of_week",
        "goal": moderate_activity_goal,
    },
    "Vigorous Activity Time": {
        "col": col3,
        "y_col_name": "vigorous_activity_time",
        "x_col_name": "day_of_week",
        "goal": vigorous_activity_goal,
    },
    "Intensity Time": {
        "col": col1,
        "y_col_name": "intensity_time",
        "x_col_name": "day_of_week",
        "goal": intensity_time_goal,
    },
    "Running Activities": {
        "col": col2,
        "y_col_name": "running_activities",
        "x_col_name": "day_of_week",
        "goal": running_activities_goal,
    },
    "Running Distance": {
        "col": col3,
        "y_col_name": "running_distance",
        "x_col_name": "day_of_week",
        "goal": running_distance_goal,
    },
}

for key, value in plots.items():
    with value["col"]:
        st.markdown(f"#### {key}")
        bar_plot_weekly_df(
            df_week,
            y_col_name=value["y_col_name"],
            x_col_name=value["x_col_name"],
            show_x_label=False,
            show_y_label=False,
            show_h_line=True,
            h_line_value=value["goal"],
            line_color="red",
            bar_color="#ff9393",
        )

# -----------------------------------------------------------------------------
# Gauges
# -----------------------------------------------------------------------------

st.markdown("### Activity Overview")

# Create sliders in columns
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.metric(
        label="Average daily steps & difference with goal:",
        value=df_week["steps"].mean().round(2),
        delta=df_week["steps"].mean().round() - step_goal,
        delta_color="normal",
    )

with col2:
    st.metric(
        label="Average daily distance & difference with goal:",
        value=df_week["distance"].mean().round(2),
        delta=df_week["distance"].mean().round() - distance_goal,
        delta_color="normal",
    )

with col3:
    st.metric(
        label="Average daily calories & difference with goal:",
        value=df_week["calories"].mean().round(2),
        delta=df_week["calories"].mean().round() - calories_goal,
        delta_color="normal",
    )


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# To do
# - colors parameter for bar graph
# - Gauge objective
# - Change to monday previous week
# -----------------------------------------------------------------------------


# # Section title
# st.markdown("## Activity metrics")

# # Create sliders in columns
# col1, col2, col3 = st.columns(3, gap="large")

# step_goal = col1.slider(
#     "Steps goal", min_value=0, max_value=20000, value=8000, step=500
# )
# distance_goal = col2.slider("Distance goal", min_value=0, max_value=20, value=8, step=1)
# calories_goal = col3.slider(
#     "Calories goal", min_value=0, max_value=4000, value=2000, step=100
# )

# with col1:
#     st.markdown("#### Steps")
#     bar_plot_weekly_df(
#         df_week,
#         y_col_name="steps",
#         x_col_name="day_of_week",
#         show_x_label=False,
#         show_y_label=False,
#         show_h_line=True,
#         h_line_value=step_goal,
#         line_color="red",
#         bar_color="#ff9393",
#     )

# with col2:
#     st.markdown("#### Distance (km)")
#     bar_plot_weekly_df(
#         df_week,
#         y_col_name="distance",
#         x_col_name="day_of_week",
#         show_x_label=False,
#         show_y_label=False,
#         show_h_line=True,
#         h_line_value=distance_goal,
#         line_color="red",
#         bar_color="#ff9393",
#     )

# with col3:
#     st.markdown("#### Calories")
#     bar_plot_weekly_df(
#         df_week,
#         y_col_name="calories",
#         x_col_name="day_of_week",
#         show_x_label=False,
#         show_y_label=False,
#         show_h_line=True,
#         h_line_value=calories_goal,
#         line_color="red",
#         bar_color="#ff9393",
#     )
