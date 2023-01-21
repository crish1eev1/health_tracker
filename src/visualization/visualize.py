import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

import os
import random

# -----------------------------------------------------------------------------
# Importing Data
# -----------------------------------------------------------------------------

# Set the directory containing the clean table files
folder_path = "../../data/processed/"

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

print("\n")


# -----------------------------------------------------------------------------
# Renaming dataframes
# -----------------------------------------------------------------------------

# Monitoring data recorded every few minutes (stress, heart rate and respiratory rate)
df_garmin_monitoring = dataframes["garmin_monitoring"]

df_garmin_monitoring_resampled = dataframes["garmin_monitoring_resampled"]

# -----------------------------------------------------------------------------
# Adjust plot settings
# -----------------------------------------------------------------------------

mpl.style.use("seaborn-v0_8-deep")
mpl.rcParams["figure.figsize"] = (20, 5)
mpl.rcParams["figure.dpi"] = 100


# -----------------------------------------------------------------------------
# Plot single columns
# -----------------------------------------------------------------------------


def plot_random_column(df, column, period):
    # Select the column(s) to use for filtering based on the selected period
    if period == "day":
        columns = ["year", "month", "day"]
    elif period == "week":
        columns = ["year", "week_of_year"]
    elif period == "month":
        columns = ["year", "month"]
    elif period == "year":
        columns = ["year"]
    else:
        raise ValueError("Invalid period")

    # Create a list of tuples containing all unique combinations of the selected columns
    combinations = list(df[columns].drop_duplicates().values)

    # Select a random combination from the list
    combination = random.choice(combinations)

    # Filter the dataframe by the selected combination
    for i, col in enumerate(columns):
        df = df[df[col] == combination[i]]

    # Get the start and end dates for the selected time period
    start_date = df.index[0].strftime("%Y-%m-%d")
    end_date = df.index[-1].strftime("%Y-%m-%d")

    # Plot the specified column using the index as the x-axis
    df[column].plot(kind="line")

    # Set the plot title to include the start and end dates
    plt.title(f"{column} from {start_date} to {end_date}")

    plt.show()


plot_random_column(df_garmin_monitoring, "stress", "day")

plot_random_column(df_garmin_monitoring_resampled, "stress", "day")


# Calculate the proportion of NaN values in each column
nan_proportion1 = df_garmin_monitoring["rr"].isnull().mean()
nan_proportion2 = df_garmin_monitoring_resampled["rr"].isnull().mean()
