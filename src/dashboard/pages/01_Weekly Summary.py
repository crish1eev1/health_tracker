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
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import altair as alt


import os
from datetime import date, timedelta

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

df_days_active = df_days[["steps", "distance", "calories", "day_of_week"]]

# -----------------------------------------------------------------------------
# Page Title & Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Weekly Overview",
    page_icon=":dart:",
    layout="wide",
    menu_items={
        "Get help": "https://www.linkedin.com/in/christophe-level",
        "About": "# This is a personal project. Visit my website for other projects: https://crish1eev1.github.io/",
    },
)

st.markdown("# Weekly Results :dart:")

# -----------------------------------------------------------------------------
# Filtering Options
# -----------------------------------------------------------------------------

# Find the Monday that is closest to today but not in the future
now = date.today()
closest_monday = now - timedelta(days=now.weekday())
if closest_monday > now:
    closest_monday -= timedelta(days=7)

week_start_date = st.date_input(
    "Choose a start date for the week:",
    value=closest_monday,
    key="date",
)
week_start_date = pd.to_datetime(week_start_date).date()


# Create columns
col1, col2, col3 = st.columns(3)

# Place sliders in columns
step_goal = col1.slider(
    "Steps goal", min_value=0, max_value=20000, value=8000, step=500
)
distance_goal = col2.slider("Distance goal", min_value=0, max_value=20, value=8, step=1)
calories_goal = col3.slider(
    "Calories goal", min_value=0, max_value=4000, value=2000, step=100
)


# -----------------------------------------------------------------------------
# Weekly activity overview
# -----------------------------------------------------------------------------

# Create a function to select the data
def select_weekly_df(week_start_date):
    week_end_date = week_start_date + pd.DateOffset(days=6)
    week_end_date = pd.to_datetime(week_end_date).date()
    df_week = df_days_active.loc[week_start_date:week_end_date]
    df_week = df_week.reindex()
    return df_week


# Create a function to plot the data
def bar_plot2_weekly_df(
    df,
    y_col_name,
    x_col_name,
    x_label="day_of_week",
    show_x_label=True,
    y_label="quantity",
    show_y_label=True,
    show_h_line=False,
    h_line_value=None,
):
    if week_start_date.weekday() != 0:
        st.warning("Monday is the only valid choice. Please select a Monday.")
    else:
        # Create the chart
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
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
        )
        # Display the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)


# Create a function to plot the data
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
):
    if week_start_date.weekday() != 0:
        st.warning("Monday is the only valid choice. Please select a Monday.")
    else:
        # Create the chart
        chart = alt.Chart(df)
        if show_h_line and h_line_value is not None:
            line = (
                alt.Chart(pd.DataFrame({"y": [h_line_value]}))
                .mark_rule(color="red", strokeWidth=2, opacity=0.5, strokeDash=[4, 4])
                .encode(y="y")
            )
        chart = chart.mark_bar().encode(
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
# Layout
# -----------------------------------------------------------------------------

st.markdown("## Weekly Activities")

col1, col2, col3 = st.columns(3, gap="large")

df_week = select_weekly_df(week_start_date)

with col1:
    st.markdown("#### Steps")
    bar_plot_weekly_df(
        df_week,
        y_col_name="steps",
        x_col_name="day_of_week",
        show_x_label=False,
        show_y_label=False,
        show_h_line=True,
        h_line_value=step_goal,
    )

with col2:
    st.markdown("#### Distance (km)")
    bar_plot_weekly_df(
        df_week,
        y_col_name="distance",
        x_col_name="day_of_week",
        show_x_label=False,
        show_y_label=False,
        show_h_line=True,
        h_line_value=distance_goal,
    )

with col3:
    st.markdown("#### Calories")
    bar_plot_weekly_df(
        df_week,
        y_col_name="calories",
        x_col_name="day_of_week",
        show_x_label=False,
        show_y_label=False,
        show_h_line=True,
        h_line_value=calories_goal,
    )


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# User filters
# -----------------------------------------------------------------------------

# x = st.slider(
#     "Select the last number of days to view :point_down:",
#     min_value=7,
#     max_value=365,
#     value=7,
# )  # this is a widget
# st.write("Last", x, "days shown")


# # Select the last 7 days of data from the 'df_days' dataframe
# df_days_active = df_days[
#     [
#         "hr_max",
#         "steps",
#         "distance",
#         "calories",
#         "moderate_activity_time",
#         "vigorous_activity_time",
#         "intensity_time",
#     ]
# ].tail(x)

# # Convert the day index to ensure it shows only the day (not the time) on streamlit
# df_days_active = df_days_active.reset_index()
# df_days_active["day"] = df_days_active["day"].dt.date
# df_days_active = df_days_active.set_index("day")

# # Convert the columns 'hr_max', 'steps' and 'calories' to integers
# df_days_active[["hr_max", "steps", "calories"]] = df_days_active[
#     ["hr_max", "steps", "calories"]
# ].astype(int)

# # Format the 'distance' column to show one decimal place
# df_days_active["distance"] = df_days_active["distance"].apply("{:,.1f}".format)

# # Convert the 'moderate_activity_time', 'vigorous_activity_time', 'intensity_time' columns to seconds
# df_days_active["moderate_activity_time"] = df_days_active[
#     "moderate_activity_time"
# ].dt.total_seconds()

# df_days_active["vigorous_activity_time"] = df_days_active[
#     "vigorous_activity_time"
# ].dt.total_seconds()

# df_days_active["intensity_time"] = df_days_active["intensity_time"].dt.total_seconds()

# # Convert the seconds to string format
# df_days_active["moderate_activity_time"] = df_days_active[
#     "moderate_activity_time"
# ].apply(lambda x: str(timedelta(seconds=x)))

# df_days_active["vigorous_activity_time"] = df_days_active[
#     "vigorous_activity_time"
# ].apply(lambda x: str(timedelta(seconds=x)))

# df_days_active["intensity_time"] = df_days_active["intensity_time"].apply(
#     lambda x: str(timedelta(seconds=x))
# )

# # Use Streamlit to display the dataframe using the 'st.dataframe' method
# st.write("### st.dataframe method:")
# st.dataframe(df_days_active.style.highlight_max(axis=0), width=2000)

# # Use Streamlit to display the dataframe using the 'st.table' method
# st.write("### st.table method:")
# st.table(df_days_active.style.highlight_max(axis=0))


# st.bar_chart(df_days_active, y="steps")
