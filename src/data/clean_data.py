# -----------------------------------------------------------------------------
# SCRIPT CLEAN_DATA.PY DESCRIPTION
# Input: Pickle and CSV files of potentially useful tables (data/raw)
# Output: Pickle and CSV files of clean tables (data/interim)
# -----------------------------------------------------------------------------
import pandas as pd

import os

# -----------------------------------------------------------------------------
# Importing the raw data
# -----------------------------------------------------------------------------
print("\n_____Importing the data_____")
folder_path = "../../data/raw/"

pickle_files = [f for f in os.listdir(folder_path) if f.endswith(".pkl")]

dataframes = {}
for file in pickle_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_pickle(file_path)
    dataframes[os.path.splitext(file)[0]] = df


# -----------------------------------------------------------------------------
# Exploring the data
# -----------------------------------------------------------------------------

# Checking initial dataframes shapes:
print("Dataframes initial shapes: ")
for df_name in dataframes:
    shape = dataframes[df_name].shape
    print(f"  {df_name}: {shape}")


# -----------------------------------------------------------------------------
# Deleting dataframes if it's confirmed they are similar
# -----------------------------------------------------------------------------
print("\n_____Deleting duplicated dataframes_____")
# Create a list of the keys of the dataframes to be compared
keys = [
    "garmin_summary.db_days_summary",
    "summary.db_days_summary",
    "garmin_summary.db_weeks_summary",
    "garmin_summary.db_weeks_summary",
    "garmin_summary.db_months_summary",
    "summary.db_months_summary",
    "garmin_summary.db_years_summary",
    "summary.db_years_summary",
]

# Initialize the variable to assume that the dataframes are similar
summary_dataframes_similar_hypothesis = True

# Iterate through the keys in pairs
for i in range(0, len(keys), 2):
    key1 = keys[i]
    key2 = keys[i + 1]
    if not dataframes[key1].equals(dataframes[key2]):
        print(f"{key1} and {key2} dataframes are not equal.")
        summary_dataframes_similar_hypothesis = False

# If the dataframes are similar, delete them from the dictionary
if summary_dataframes_similar_hypothesis:
    del dataframes["summary.db_days_summary"]
    del dataframes["summary.db_weeks_summary"]
    del dataframes["summary.db_months_summary"]
    del dataframes["summary.db_years_summary"]
    print("Duplicated dataframes deleted.")


# -----------------------------------------------------------------------------
# Removing empty columns from all dataframes
# -----------------------------------------------------------------------------
print("\n_____Removing empty columns from all dataframes_____")
print("Checking for null columns:")
# Initialize a counter for the number of null columns removed
null_columns_counter = 0
# Iterate over the dataframes
for df_name in dataframes:
    # Identify the null columns in the current dataframe
    null_columns = dataframes[df_name].columns[dataframes[df_name].isnull().all()]
    # Print the name of the dataframe and the null columns
    print(f"  {df_name}:")
    for column in null_columns:
        print(f"     - {column}")

    # Drop the null columns from the dataframe
    dataframes[df_name].drop(null_columns, axis=1, inplace=True)

    # Increment counter
    null_columns_counter += len(null_columns)
# Print number of columns removed
print(f"Empty columns removed: {null_columns_counter}")


# -----------------------------------------------------------------------------
# Removing rows before 27th December 2022 for all dataframes (empty before that)
# -----------------------------------------------------------------------------
print("\n_____Removing empty rows from before wearing the watch_____")
# Create a list of the keys of the dataframes whose 'day' column needs to be converted
keys_day = [
    "garmin.db_daily_summary",
    "garmin.db_sleep",
    "garmin_summary.db_days_summary",
]
# Iterate through the keys in the list
for key in keys_day:
    # Convert the 'day' column to datetime type
    dataframes[key]["day"] = pd.to_datetime(dataframes[key]["day"])
# Create a list of the keys of the dataframes whose 'timestamp' column needs to be converted
keys_timestamp = [
    "garmin.db_stress",
    "garmin_monitoring.db_monitoring_hr",
    "garmin_monitoring.db_monitoring_rr",
    "garmin_summary.db_intensity_hr",
]
# Iterate through the keys in the list
for key in keys_timestamp:
    # Convert the 'timestamp' column to datetime type
    dataframes[key]["timestamp"] = pd.to_datetime(dataframes[key]["timestamp"])

# Set the cutoff date
cutoff_date = pd.to_datetime("2019-12-27")


def filter_and_drop(dataframes, keys, column):
    """
    Filter the rows of the dataframes in the 'dataframes' dictionary based on the 'cutoff_date'
    and drop the filtered rows from the original dataframe.

    Parameters:
    dataframes: a dictionary of dataframes
    keys: a list of keys of the dataframes to be filtered
    column: a string representing the name of the column used to filter the rows

    Returns:
    None
    """
    # Iterate through the keys in the list
    for key in keys:
        # Filter the rows based on the date
        filtered_df = dataframes[key][dataframes[key][column] < cutoff_date]
        # Drop the filtered rows from the original dataframe
        dataframes[key].drop(filtered_df.index, inplace=True)


# Create a list of the keys of the dataframes to be filtered
keys = ["garmin.db_daily_summary", "garmin.db_sleep"]
# Filter the rows based on the 'day' column
filter_and_drop(dataframes, keys, "day")

# Create a list of the keys of the dataframes to be filtered
keys = [
    "garmin.db_stress",
    "garmin_monitoring.db_monitoring_hr",
    "garmin_monitoring.db_monitoring_rr",
    "garmin_summary.db_intensity_hr",
]
# Filter the rows based on the 'timestamp' column
filter_and_drop(dataframes, keys, "timestamp")

print(f"Empty data from before {cutoff_date} removed")


# -----------------------------------------------------------------------------
# Checking for duplicates
# -----------------------------------------------------------------------------
print("\n_____Checking for duplicates_____")


def check_for_duplicates(df_dict):
    for key, df in df_dict.items():
        duplicates = df[df.duplicated()]
        if not duplicates.empty:
            print(
                f"\n\n !!! WARNING: Duplicate rows found in dataframe {key}:\n{duplicates}"
            )
        else:
            print(f"No duplicate rows found in dataframe {key}.")


check_for_duplicates(df_dict=dataframes)

# I'm not performing any blind treatment here but raising a warning if duplicates are found

# -----------------------------------------------------------------------------
# Fixing data types for dates and time
# -----------------------------------------------------------------------------
print("\n_____Fixing data types for dates and time_____")

column_keys = {
    "start": ["garmin.db_sleep"],
    "end": ["garmin.db_sleep"],
    "start_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "stop_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "timestamp": ["garmin_activities.db_activity_records"],
}

format_string = "%Y-%m-%d %H:%M:%S"

for column, keys in column_keys.items():
    for key in keys:
        dataframes[key][column] = pd.to_datetime(
            dataframes[key][column], format=format_string
        )
        print(f"column {column} from {key} converted to datetime")


column_keys = {
    "total_sleep": ["garmin.db_sleep"],
    "deep_sleep": ["garmin.db_sleep"],
    "light_sleep": ["garmin.db_sleep"],
    "rem_sleep": ["garmin.db_sleep"],
    "awake": ["garmin.db_sleep"],
    "moderate_activity_time": [
        "garmin.db_daily_summary",
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "vigorous_activity_time": [
        "garmin.db_daily_summary",
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "intensity_time_goal": [
        "garmin.db_daily_summary",
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "elapsed_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "moving_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "hrz_1_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "hrz_2_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "hrz_3_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "hrz_4_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "hrz_5_time": [
        "garmin_activities.db_activities",
        "garmin_activities.db_activity_laps",
    ],
    "avg_pace": ["garmin_activities.db_steps_activities"],
    "avg_moving_pace": ["garmin_activities.db_steps_activities"],
    "max_pace": ["garmin_activities.db_steps_activities"],
    "avg_ground_contact_time": ["garmin_activities.db_steps_activities"],
    "intensity_time": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "sleep_avg": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "sleep_min": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "sleep_max": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "rem_sleep_avg": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "rem_sleep_min": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
    "rem_sleep_max": [
        "garmin_summary.db_days_summary",
        "garmin_summary.db_months_summary",
        "garmin_summary.db_years_summary",
        "garmin_summary.db_weeks_summary",
    ],
}


for column, keys in column_keys.items():
    for key in keys:
        dataframes[key][column] = pd.to_timedelta(dataframes[key][column])
        print(f"column {column} from {key} converted to timedelta")


# -----------------------------------------------------------------------------
# Fixing other datatypes
# -----------------------------------------------------------------------------
print("\n_____Converting other data types_____")
# Iterate over the DataFrames in the dictionary
for key, df in dataframes.items():
    # Select the object columns to convert
    obj_cols = df.select_dtypes(["object"]).columns
    # Iterate over the object columns
    for col in obj_cols:
        # Convert the column to the best possible data type
        df[col] = df[col].apply(pd.to_numeric, errors="ignore")
        # Check if the data type of the column has changed
        if df[col].dtype != "object":
            # Print the column name and DataFrame name
            print(f"Column '{col}' in DataFrame '{key}' converted to numeric")

# Iterate over the DataFrames in the dictionary
for key, df in dataframes.items():
    # Select the object columns to convert
    obj_cols = df.select_dtypes(["object"]).columns
    # Iterate over the object columns
    for col in obj_cols:
        # Convert the column to the best possible data type
        df[col] = df[col].apply(pd.to_datetime, errors="ignore")
        # Check if the data type of the column has changed
        if df[col].dtype != "object":
            # Print the column name and DataFrame name
            print(f"Column '{col}' in DataFrame '{key}' converted to datetime")

# Iterate over the DataFrames in the dictionary
for key, df in dataframes.items():
    # Select the object columns to convert
    obj_cols = df.select_dtypes(["object"]).columns
    # Iterate over the object columns
    for col in obj_cols:
        # Convert the column to the best possible data type
        df[col] = df[col].astype(str)

# -----------------------------------------------------------------------------
# Removing unnecessary columns
# -----------------------------------------------------------------------------
print("\n_____Removing columns containing only one unique value_____")
# Removing columns with only one unique value
for key, df in dataframes.items():
    print(f"\n{key}:")
    for col in df.columns:
        if df[col].nunique() == 1:
            df.drop(col, axis=1, inplace=True)
            print(f"  - column {col} removed")

# Removing other unnecessary columns manually
print("\n_____Removing unnecessary columns after manual check_____")
to_remove = {
    "garmin.db_daily_summary": ["step_goal"],
    "garmin_summary.db_days_summary": [
        "rhr_min",
        "rhr_max",
        "steps_goal",
        "sleep_min",
        "sleep_max",
        "rem_sleep_min",
        "rem_sleep_max",
        "sweat_loss_avg",
    ],
    "garmin_summary.db_weeks_summary": ["steps_goal", "floors_goal", "hydration_goal"],
    "garmin_summary.db_months_summary": ["steps_goal", "floors_goal", "hydration_goal"],
    "garmin_summary.db_years_summary": ["steps_goal", "floors_goal", "hydration_goal"],
}

for key, df in dataframes.items():
    if key in to_remove:
        columns = to_remove[key]
        df.drop(columns, axis=1, inplace=True)
        print(f"\n{key}:")
        print(f"  - columns {columns} removed")


# -----------------------------------------------------------------------------
# Adjusting time
# -----------------------------------------------------------------------------
print("\n_____Adjusting tables from time zones_____")
# Get the maximum values of the 'timestamp' column
max_timestamp_hr = dataframes["garmin_monitoring.db_monitoring_hr"]["timestamp"].max()
max_timestamp_stress = dataframes["garmin.db_stress"]["timestamp"].max()
max_timestamp_rr = dataframes["garmin_monitoring.db_monitoring_rr"]["timestamp"].max()


# Calculate the difference between the maximum values
diff1 = max_timestamp_hr - max_timestamp_stress
diff2 = max_timestamp_rr - max_timestamp_stress

# Check if the difference is equal to one hour
if diff1 == pd.Timedelta(hours=1) and diff2 == pd.Timedelta(hours=1):
    print(
        "monitoring_stress dataframe is 1 hour behind the other two dataframes. Performing adjustment..."
    )

    # Add one hour to the 'timestamp' column
    dataframes["garmin.db_stress"]["timestamp"] = dataframes["garmin.db_stress"][
        "timestamp"
    ].apply(lambda x: x + pd.DateOffset(hours=1))
    print("Adjustment performed. 1 hour added.")
else:
    print("monitoring_stress dataframe is not 1 hour behind the other two dataframes.")
    print("!!!!! \n !!!!! \n !!!!!")

print("\n")

# -----------------------------------------------------------------------------
# Sorting and re-indexing the data
# -----------------------------------------------------------------------------


dataframes["garmin.db_daily_summary"] = (
    dataframes["garmin.db_daily_summary"]
    .sort_values(by="day", ascending=True)
    .reset_index(drop=True)
)

dataframes["garmin.db_sleep"] = (
    dataframes["garmin.db_sleep"]
    .sort_values(by="day", ascending=True)
    .reset_index(drop=True)
)


# -----------------------------------------------------------------------------
# Checking final dataframes shape
# -----------------------------------------------------------------------------
print("\n_____Checking final dataframes shape_____")

# Checking final dataframes shapes
total_rows = 0
total_columns = 0

print("Dataframes final shapes:")
for df_name in dataframes:
    shape = dataframes[df_name].shape
    total_rows += shape[0]
    total_columns += shape[1]
    print(f"{df_name}: {shape}")

# -----------------------------------------------------------------------------
# Exporting the results
# -----------------------------------------------------------------------------
print("\n_____Exporting the results_____")

for key, df in dataframes.items():
    # Save the dataframe as a pickle file
    df.to_pickle(f"../../data/interim/{key}.pkl")
    # Save the dataframe as a CSV file
    df.to_csv(f"../../data/interim/{key}.csv")

print(f"Tables exported: {len(dataframes)}")
print(f"Total rows: {total_rows}")
print(f"Total columns: {total_columns}")
