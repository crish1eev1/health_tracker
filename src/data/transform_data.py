# -----------------------------------------------------------------------------
# SCRIPT: transform_data.py
# DESCRIPTION:
#   Imports pickle and CSV files of clean tables from the "data/interim" directory
#   and creates pickle and CSV files of aggregated workfiles in the "data/processed" directory.
# INPUT: Pickle and CSV files in the "data/interim" directory
# OUTPUT: Pickle and CSV files in the "data/processed" directory
# -----------------------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os

# -----------------------------------------------------------------------------
# Importing Data
# -----------------------------------------------------------------------------
print("\n_____Importing the data_____")

# Set the directory containing the clean table files
folder_path = "../../data/interim/"

# Get the file paths of all pickle files in the directory
pickle_files = [f for f in os.listdir(folder_path) if f.endswith(".pkl")]

# Create a dictionary to store the dataframes
dataframes = {}

# Iterate over the file paths
for file in pickle_files:
    # Construct the full file path
    file_path = os.path.join(folder_path, file)

    # Load the dataframe from the file
    df = pd.read_pickle(file_path)

    # Add the dataframe to the dictionary using the file name as the key
    dataframes[os.path.splitext(file)[0]] = df
    print(f"{file} imported")


# -----------------------------------------------------------------------------
# Renaming dataframes
# -----------------------------------------------------------------------------

# Monitoring data recorded every few minutes (stress, heart rate and respiratory rate)
df_garmin_monitoring_stress = dataframes["garmin.db_stress"]
df_garmin_monitoring_hr = dataframes["garmin_monitoring.db_monitoring_hr"]
df_garmin_monitoring_rr = dataframes["garmin_monitoring.db_monitoring_rr"]
df_garmin_monitoring_intensity = dataframes["garmin_summary.db_intensity_hr"]

# Daily data
df_garmin_daily_summary = dataframes["garmin.db_daily_summary"]
df_garmin_daily_sleep = dataframes["garmin.db_sleep"]

# Summary data
df_garmin_days_summary = dataframes["garmin_summary.db_days_summary"]
df_garmin_weeks_summary = dataframes["garmin_summary.db_weeks_summary"]
df_garmin_months_summary = dataframes["garmin_summary.db_months_summary"]
df_garmin_years_summary = dataframes["garmin_summary.db_years_summary"]

# Activity data (based on a recorded activity)
df_garmin_activities = dataframes["garmin_activities.db_activities"]
df_garmin_activity_laps = dataframes["garmin_activities.db_activity_laps"]
df_garmin_activity_records = dataframes["garmin_activities.db_activity_records"]
df_garmin_activity_steps = dataframes["garmin_activities.db_steps_activities"]


# -----------------------------------------------------------------------------
# Merging monitoring dataframes into a single dataframe
# -----------------------------------------------------------------------------
print("\n_____Merging monitoring data into a single table_____")

# Find the start and end timestamps
start_timestamp = min(
    df_garmin_monitoring_stress["timestamp"].min(),
    df_garmin_monitoring_hr["timestamp"].min(),
    df_garmin_monitoring_rr["timestamp"].min(),
)
end_timestamp = max(
    df_garmin_monitoring_stress["timestamp"].max(),
    df_garmin_monitoring_hr["timestamp"].max(),
    df_garmin_monitoring_rr["timestamp"].max(),
)

# Create a new dataframe with a timestamp column ranging from the start to the end timestamp, with one minute intervals
df_garmin_monitoring = pd.DataFrame(
    {"timestamp": pd.date_range(start_timestamp, end_timestamp, freq="min")}
)

# Merge the dataframes
df_garmin_monitoring = df_garmin_monitoring.merge(
    df_garmin_monitoring_stress, on="timestamp", how="left"
)
df_garmin_monitoring = df_garmin_monitoring.merge(
    df_garmin_monitoring_hr, on="timestamp", how="left"
)
df_garmin_monitoring = df_garmin_monitoring.merge(
    df_garmin_monitoring_rr, on="timestamp", how="left"
)

# Printing info
print("monitoring data merged.")

# -----------------------------------------------------------------------------
# Merging daily dataframes into a single dataframe
# -----------------------------------------------------------------------------
print("\n_____Merging daily data into a single table_____")

# Removing columns (done after performing some explorations)
df_garmin_daily_summary.drop(
    ["intensity_time_goal", "calories_bmr", "calories_active"], axis=1, inplace=True
)

df_garmin_days_summary.drop(
    [
        "intensity_time_goal",
        "calories_bmr_avg",
        "calories_active_avg",
        "calories_avg",
        "rhr_avg",
        "hr_min",
        "hr_max",
        "moderate_activity_time",
        "vigorous_activity_time",
        "steps",
        "stress_avg",
        "rr_waking_avg",
        "rr_max",
        "rr_min",
        "bb_max",
        "bb_min",
        "sweat_loss",
        "sleep_avg",
        "rem_sleep_avg",
    ],
    axis=1,
    inplace=True,
)


# Find the start and end timestamps
start_timestamp = min(
    df_garmin_daily_summary["day"].min(),
    df_garmin_days_summary["day"].min(),
    df_garmin_daily_sleep["day"].min(),
)
end_timestamp = max(
    df_garmin_daily_summary["day"].max(),
    df_garmin_days_summary["day"].max(),
    df_garmin_daily_sleep["day"].max(),
)


# Create a new dataframe with a day column ranging from the start to the end day, with one day intervals
df_garmin_days = pd.DataFrame(
    {"day": pd.date_range(start_timestamp, end_timestamp, freq="D")}
)

# Merging
df_garmin_days = df_garmin_days.merge(df_garmin_daily_summary, on="day", how="left")

df_garmin_days = df_garmin_days.merge(
    df_garmin_days_summary,
    on="day",
    how="left",
    suffixes=("_duplicate_left", "_duplicate_right"),
)

df_garmin_days = df_garmin_days.merge(
    df_garmin_daily_sleep,
    on="day",
    how="left",
    suffixes=("_duplicate_left", "_duplicate_right"),
)


# Get list of all column names
columns = df_garmin_days.columns

# Create an empty list to store identical column names
identical_columns = []

# Iterate over all column pairs
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):
        # Compare the values in the two columns
        if df_garmin_days[columns[i]].equals(df_garmin_days[columns[j]]):
            # Add the identical column names to the list
            identical_columns.append(columns[j])

# Remove duplicate column names from the list
identical_columns = list(set(identical_columns))

# Drop identical columns from the DataFrame
df_garmin_days.drop(identical_columns, axis=1, inplace=True)

print("daily data merged.")

# -----------------------------------------------------------------------------
# Filtering df_garmin_activities to running only and keeping useful columns
# -----------------------------------------------------------------------------
print("\n_____Filter activities dataframe to running only_____")

df_garmin_running = df_garmin_activities[df_garmin_activities["sport"] == "running"]
df_garmin_running.drop(["avg_rr", "max_rr"], axis=1, inplace=True)

m = df_garmin_activity_laps["activity_id"].isin(df_garmin_running["activity_id"])
df_garmin_running_laps = df_garmin_activity_laps[m]

m = df_garmin_activity_records["activity_id"].isin(df_garmin_running["activity_id"])
df_garmin_running_records = df_garmin_activity_records[m]

m = df_garmin_activity_steps["activity_id"].isin(df_garmin_running["activity_id"])
df_garmin_running_steps = df_garmin_activity_steps[m]

print("filters applied.")

# -----------------------------------------------------------------------------
# Shifting night data to the previous day
# -----------------------------------------------------------------------------
"""
I decided to take the convention to associate the night data with the previous day.
For example, if someone wakes up on Tuesday morning, I think of the sleep period as being part of Monday.
"""
print("\n_____Shifting night data to the previous day_____")

df_garmin_days["start"] = df_garmin_days["start"].shift(-1)
df_garmin_days["end"] = df_garmin_days["end"].shift(-1)
df_garmin_days["total_sleep"] = df_garmin_days["total_sleep"].shift(-1)
df_garmin_days["deep_sleep"] = df_garmin_days["deep_sleep"].shift(-1)
df_garmin_days["light_sleep"] = df_garmin_days["light_sleep"].shift(-1)
df_garmin_days["rem_sleep"] = df_garmin_days["rem_sleep"].shift(-1)
df_garmin_days["awake"] = df_garmin_days["awake"].shift(-1)
df_garmin_days["avg_rr"] = df_garmin_days["awake"].shift(-1)

print("night data shifted.")


# -----------------------------------------------------------------------------
# Using HH:MM:SS format for sleeping and waking times
# -----------------------------------------------------------------------------
print("\n_____Converting start and end sleeping time_____")

from datetime import datetime

default_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
df_garmin_days["sleep_start_time"] = df_garmin_days["start"].dt.time.where(
    df_garmin_days["start"].notna(), default_time
)
df_garmin_days["sleep_end_time"] = df_garmin_days["end"].dt.time.where(
    df_garmin_days["end"].notna(), default_time
)


df_garmin_days["sleep_start_timedelta"] = df_garmin_days["sleep_start_time"].apply(
    lambda x: pd.to_timedelta(x.strftime("%H:%M:%S"))
)
df_garmin_days["sleep_end_timedelta"] = df_garmin_days["sleep_end_time"].apply(
    lambda x: pd.to_timedelta(x.strftime("%H:%M:%S"))
)

df_garmin_days["sleep_start_timedelta_seconds"] = df_garmin_days[
    "sleep_start_timedelta"
].dt.total_seconds()
df_garmin_days["sleep_start_timedelta_seconds"] = df_garmin_days.apply(
    lambda row: row["sleep_start_timedelta_seconds"] - 86400
    if row["sleep_start_timedelta_seconds"] > 43200
    else row["sleep_start_timedelta_seconds"],
    axis=1,
)

df_garmin_days["sleep_end_timedelta_seconds"] = df_garmin_days[
    "sleep_end_timedelta"
].dt.total_seconds()
df_garmin_days["sleep_end_timedelta_seconds"] = df_garmin_days.apply(
    lambda row: row["sleep_end_timedelta_seconds"] - 86400
    if row["sleep_end_timedelta_seconds"] > 43200
    else row["sleep_end_timedelta_seconds"],
    axis=1,
)

df_garmin_days["start_sleep"] = df_garmin_days["start"]
df_garmin_days["end_sleep"] = df_garmin_days["end"]

del df_garmin_days["start"]
del df_garmin_days["end"]
del df_garmin_days["sleep_start_time"]
del df_garmin_days["sleep_end_time"]
del df_garmin_days["sleep_start_timedelta"]
del df_garmin_days["sleep_end_timedelta"]

print("data converted.")

df_garmin_days.info()


# -----------------------------------------------------------------------------
# Adding datetime columns to monitoring dataframe
# -----------------------------------------------------------------------------
print("\n_____Adding datetime columns_____")

# Add new columns for the year, month, day of the week, and week of the year
df_garmin_monitoring["year"] = df_garmin_monitoring["timestamp"].dt.year
df_garmin_monitoring["month"] = df_garmin_monitoring["timestamp"].dt.month
df_garmin_monitoring["day"] = df_garmin_monitoring["timestamp"].dt.day
df_garmin_monitoring["day_of_week"] = df_garmin_monitoring["timestamp"].dt.weekday
df_garmin_monitoring["week_of_year"] = (
    df_garmin_monitoring["timestamp"].dt.isocalendar().week
)

# Printing info
print("Datetime Columns added to monitoring table.")

# -----------------------------------------------------------------------------
# Re-indexing dataframes
# -----------------------------------------------------------------------------

df_garmin_monitoring = df_garmin_monitoring.set_index("timestamp")
df_garmin_days = df_garmin_days.set_index("day")

# -----------------------------------------------------------------------------
# Inject values to monitoring dataframe using linear interpolation
# -----------------------------------------------------------------------------
print("\n_____Injecting values via linear interpolation_____")

# create the 'in_activity' column based on stress -1 (non recorded) and -2 (recorded) data
df_garmin_monitoring["in_activity"] = df_garmin_monitoring["stress"].apply(
    lambda x: 2 if x == -2 else (1 if x == -1 else 0)
)

# list of columns you want to interpolate
columns = ["stress", "heart_rate", "rr"]

# iterate over columns
for col in columns:
    # get boolean mask for original null values
    null_mask = df_garmin_monitoring[col].isnull()

    # interpolate values using limit parameter
    interpolated_values = df_garmin_monitoring[col].interpolate(
        method="linear", limit=4, limit_direction="both"
    )

    # update original column with interpolated values
    df_garmin_monitoring[col] = interpolated_values

    # create new column with injected values mask
    df_garmin_monitoring[f"{col}_injected"] = null_mask & ~interpolated_values.isnull()

    # print number of injected values
    injected_count = (null_mask & ~interpolated_values.isnull()).sum()
    print(f'Number of injected values in "{col}": {injected_count}')


# replace all negative values in stress column with NaN
df_garmin_monitoring["stress"] = df_garmin_monitoring["stress"].apply(
    lambda x: np.nan if x < 0 else x
)

# State injected = false if values in stress column is NaN
df_garmin_monitoring.loc[
    df_garmin_monitoring["stress"].isnull(), "stress_injected"
] = False


# -----------------------------------------------------------------------------
# Adding activity ids info to monitoring dataframe
# -----------------------------------------------------------------------------
print("\n_____Adding activity ids info to monitoring tables_____")

for _, activity in df_garmin_activities.iterrows():
    start_time = activity["start_time"]
    stop_time = activity["stop_time"]
    activity_id = activity["activity_id"]

    # Select rows in df_garmin_monitoring that fall within start and stop times for activity
    mask = (df_garmin_monitoring.index >= start_time) & (
        df_garmin_monitoring.index <= stop_time
    )
    df_garmin_monitoring.loc[mask, "activity_id"] = activity_id

print("Activity ids added.")

# -----------------------------------------------------------------------------
# Adding running activities main infos to daily dataframe
# -----------------------------------------------------------------------------
print("\n_____Adding running activities main infos to daily dataframe_____")

# extract day from start_time column
df_garmin_running["day"] = df_garmin_running["start_time"].dt.date

# group the df_garmin_running dataframe by the day of the start_time column
activity_count = (
    df_garmin_running.groupby("day").size().reset_index(name="running_activities")
)
activity_calories = (
    df_garmin_running.groupby("day").calories.sum().reset_index(name="running_calories")
)
activity_distance = (
    df_garmin_running.groupby("day").distance.sum().reset_index(name="running_distance")
)

# convert
activity_count["day"] = activity_count["day"].astype("datetime64")
activity_calories["day"] = activity_calories["day"].astype("datetime64")
activity_distance["day"] = activity_distance["day"].astype("datetime64")


# merge the activity_count and activity_calories to the df_garmin_days on the date
df_garmin_days = df_garmin_days.merge(
    activity_count, left_index=True, right_on="day", how="left"
)
df_garmin_days = df_garmin_days.set_index("day")
df_garmin_days = df_garmin_days.merge(
    activity_calories, left_index=True, right_on="day", how="left"
)
df_garmin_days = df_garmin_days.set_index("day")
df_garmin_days = df_garmin_days.merge(
    activity_distance, left_index=True, right_on="day", how="left"
)
df_garmin_days = df_garmin_days.set_index("day")

# fill missing values
df_garmin_days["running_activities"].fillna(0, inplace=True)
df_garmin_days["running_calories"].fillna(0, inplace=True)
df_garmin_days["running_distance"].fillna(0, inplace=True)

# removing activities columns
del df_garmin_days["activities"]
del df_garmin_days["activities_calories"]
del df_garmin_days["activities_distance"]

print("Running info added to daily.")

# -----------------------------------------------------------------------------
# Removing data from daily df when monitoring df doesn't include enough data
# -----------------------------------------------------------------------------
print("\n_____Removing data from daily for days with not enough data_____")

# Create a new column that indicates whether the row has NaN values
df_garmin_monitoring["has_nan"] = (
    df_garmin_monitoring[["stress", "heart_rate", "rr"]].isna().any(axis=1)
)


df_garmin_monitoring[df_garmin_monitoring["has_nan"] == True]

# Group the data by day and count the number of rows that have NaN values
nan_count_by_day = df_garmin_monitoring.groupby(df_garmin_monitoring.index.date)[
    "has_nan"
].sum()

# Identify the days where more than a certain threshold of data is missing
threshold = 0.5
days_with_insufficient_data = nan_count_by_day[
    nan_count_by_day > threshold * 1440
].index  # 1440 is total minute in a day


for date in days_with_insufficient_data:
    print(date)

# Remove the values for the days identified
# Keep the days but with NaN values
# rows_to_replace = df_garmin_days.index.isin(days_with_insufficient_data)
# df_garmin_days.loc[rows_to_replace, :] = np.nan

# Remove the days completely
df_garmin_days = df_garmin_days[~df_garmin_days.index.isin(days_with_insufficient_data)]

# -----------------------------------------------------------------------------
# Removing data from daily when key data is missing
# -----------------------------------------------------------------------------
# Create a new column that indicates whether the row has NaN values in the specific columns
cols_to_check = ["hr_min", "hr_max", "rhr", "steps", "start_sleep", "end_sleep"]
df_garmin_days["has_nan"] = df_garmin_days[cols_to_check].isna().any(axis=1)

# Identify the rows that have missing values in the specific columns
rows_to_replace = df_garmin_days[df_garmin_days["has_nan"] == True].index

# Replace all columns of the rows identified with NaN
df_garmin_days.loc[rows_to_replace, :] = np.nan

# Remove the values for the rows identified
df_garmin_days.drop(rows_to_replace, inplace=True)

# Drop the has_nan column from the dataframe
df_garmin_days.drop("has_nan", axis=1, inplace=True)

print("Days removed:")
for date in rows_to_replace:
    print(date)

rows_removed = len(days_with_insufficient_data) + len(rows_to_replace)

print(
    f"Total days removed: {rows_removed}/{len(df_garmin_days)} ({round(rows_removed/len(df_garmin_days)*100,2)}%)"
)


# -----------------------------------------------------------------------------
# Resampling the data
# -----------------------------------------------------------------------------
print("\n_____Resampling the data_____")

# Daily data
agg_dict = {
    col: "mean"
    for col in df_garmin_days.columns
    if col not in ["running_activities", "running_calories", "running_distance"]
}
agg_dict.update(
    {
        "running_activities": "sum",
        "running_calories": "sum",
        "running_distance": "sum",
    }
)

df_garmin_weeks = df_garmin_days.resample("W").agg(agg_dict)
df_garmin_weeks["days_resampled"] = df_garmin_days.resample("W").size()

df_garmin_months = df_garmin_days.resample("M").agg(agg_dict)
df_garmin_months["days_resampled"] = df_garmin_days.resample("M").size()

print("data resampled.")


df_garmin_days.info()

# -----------------------------------------------------------------------------
# Rounding values
# -----------------------------------------------------------------------------
print("\n_____Rounding values_____")

# Rounding to one decimal
for column in ["stress", "heart_rate"]:
    df_garmin_monitoring[column] = df_garmin_monitoring[column].round(1)

for column in [
    "hr_min",
    "hr_max",
    "rhr",
    "stress_avg",
    "distance",
    "rr_waking_avg",
    "rr_max",
    "rr_min",
    "bb_charged",
    "bb_max",
    "bb_min",
    "hr_avg",
    "inactive_hr_avg",
    "inactive_hr_min",
    "inactive_hr_max",
    "running_distance",
    "steps",
    "calories_total",
    "sweat_loss",
]:
    df_garmin_days[column] = df_garmin_days[column].round(1)
    df_garmin_weeks[column] = df_garmin_weeks[column].round(1)
    df_garmin_months[column] = df_garmin_months[column].round(1)

# Rounding to int
for column in [
    "steps",
    "calories_total",
    "running_activities",
    "running_calories",
]:
    df_garmin_days[column] = df_garmin_days[column].round()
    df_garmin_weeks[column] = df_garmin_weeks[column].round()
    df_garmin_months[column] = df_garmin_months[column].round()


# Rounding to sec
for column in [
    "moderate_activity_time",
    "vigorous_activity_time",
    "intensity_time",
    "start_sleep",
    "end_sleep",
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
    "avg_rr",
]:
    df_garmin_months[column] = df_garmin_months[column].dt.round(freq="s")
    df_garmin_weeks[column] = df_garmin_weeks[column].dt.round(freq="s")


for column in [
    "elapsed_time",
    "moving_time",
    "hrz_1_time",
    "hrz_2_time",
    "hrz_3_time",
    "hrz_4_time",
    "hrz_5_time",
]:
    df_garmin_running[column] = df_garmin_running[column].dt.round(freq="s")
    df_garmin_running_laps[column] = df_garmin_running_laps[column].dt.round(freq="s")

print("Values rounded.")


# -----------------------------------------------------------------------------
# Convert the average seconds back to time
# -----------------------------------------------------------------------------

df_garmin_days["start_sleep_time"] = pd.to_timedelta(
    df_garmin_days["sleep_start_timedelta_seconds"], unit="s"
)
del df_garmin_days["sleep_start_timedelta_seconds"]

df_garmin_weeks["start_sleep_time"] = pd.to_timedelta(
    df_garmin_weeks["sleep_start_timedelta_seconds"], unit="s"
)
del df_garmin_weeks["sleep_start_timedelta_seconds"]
del df_garmin_weeks["start_sleep"]
del df_garmin_weeks["end_sleep"]


df_garmin_months["start_sleep_time"] = pd.to_timedelta(
    df_garmin_months["sleep_start_timedelta_seconds"], unit="s"
)
del df_garmin_months["sleep_start_timedelta_seconds"]
del df_garmin_months["start_sleep"]
del df_garmin_months["end_sleep"]


# -----------------------------------------------------------------------------
# Reordering columns
# -----------------------------------------------------------------------------

#
col = df_garmin_monitoring.pop("activity_id")
df_garmin_monitoring.insert(9, "activity_id", col)
del df_garmin_monitoring["has_nan"]


#
columns_daily = [
    "hr_min",
    "inactive_hr_min",
    "rhr",
    "inactive_hr_avg",
    "hr_avg",
    "inactive_hr_max",
    "hr_max",
    "stress_avg",
    "steps",
    "distance",
    "calories_total",
    "bb_charged",
    "bb_max",
    "bb_min",
    "rr_waking_avg",
    "rr_max",
    "rr_min",
    "moderate_activity_time",
    "vigorous_activity_time",
    "intensity_time",
    "running_activities",
    "running_calories",
    "running_distance",
    "sweat_loss",
    "start_sleep",
    "end_sleep",
    "start_sleep_time",
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
    "avg_rr",
]

columns_weekly_monthly = [
    "hr_min",
    "inactive_hr_min",
    "rhr",
    "inactive_hr_avg",
    "hr_avg",
    "inactive_hr_max",
    "hr_max",
    "stress_avg",
    "steps",
    "distance",
    "calories_total",
    "bb_charged",
    "bb_max",
    "bb_min",
    "rr_waking_avg",
    "rr_max",
    "rr_min",
    "moderate_activity_time",
    "vigorous_activity_time",
    "intensity_time",
    "running_activities",
    "running_calories",
    "running_distance",
    "sweat_loss",
    "start_sleep_time",
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
    "avg_rr",
    "days_resampled",
]

df_garmin_days = df_garmin_days[columns_daily]
df_garmin_weeks = df_garmin_weeks[columns_weekly_monthly]
df_garmin_months = df_garmin_months[columns_weekly_monthly]


# -----------------------------------------------------------------------------
# Renaming columns
# -----------------------------------------------------------------------------
print("\n_____Renaming columns_____")

column_mapping = {"rr": "respiration_rate", "rr_injected": "respiration_rate_injected"}
df_garmin_monitoring.rename(columns=column_mapping, inplace=True)

column_mapping = {
    "rhr": "resting_hr",
    "rr_injected": "respiration_rate_injected",
    "calories_total": "calories",
    "avg_rr": "avg_rr_sleep",
}
df_garmin_days.rename(columns=column_mapping, inplace=True)
df_garmin_weeks.rename(columns=column_mapping, inplace=True)
df_garmin_months.rename(columns=column_mapping, inplace=True)

# column_mapping = {
#     "hr_min": "hr_min_daily_avg",
#     "hr_max": "hr_max_daily_avg",
#     "rhr": "rhr_daily_avg",
#     "stress_avg": "stress_daily_avg",
#     "steps": "steps_daily_avg",
#     "moderate_activity_time": "moderate_activity_time_daily_avg",
#     "vigorous_activity_time": "vigorous_activity_time_daily_avg",
#     "distance": "distance_daily_avg",
#     "calories_total": "calories_daily_avg",
# }
# df_garmin_months.rename(columns=column_mapping, inplace=True)

print("Columns renamed.")


# -----------------------------------------------------------------------------
# To Do
# - Transform df_garmin_running df
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Exporting the results
# -----------------------------------------------------------------------------

df_garmin_monitoring.to_pickle("../../data/processed/garmin_monitoring.pkl")
df_garmin_monitoring.to_csv("../../data/processed/garmin_monitoring.csv")

df_garmin_days.to_pickle("../../data/processed/garmin_days.pkl")
df_garmin_days.to_csv("../../data/processed/garmin_days.csv")

df_garmin_weeks.to_pickle("../../data/processed/garmin_weeks.pkl")
df_garmin_weeks.to_csv("../../data/processed/garmin_weeks.csv")

df_garmin_months.to_pickle("../../data/processed/garmin_months.pkl")
df_garmin_months.to_csv("../../data/processed/garmin_months.csv")

df_garmin_running
df_garmin_running

df_garmin_running_laps
df_garmin_running_laps

df_garmin_running_records
df_garmin_running_records

df_garmin_running_steps
df_garmin_running_steps

print("Data exported.")
