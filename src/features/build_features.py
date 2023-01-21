import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

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

df_garmin_days = dataframes["garmin_days"]
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

correlations = df_garmin_monitoring[["stress", "heart_rate", "rr"]].corr()
sns.heatmap(correlations, annot=True)

df_garmin_days.info()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


# select the timedelta columns
timedelta_columns = [
    "intensity_time",
    "total_sleep",
    "deep_sleep",
    "light_sleep",
    "rem_sleep",
    "awake",
]

# convert to numeric columns with total seconds
df_garmin_days[timedelta_columns] = df_garmin_days[timedelta_columns].apply(
    lambda x: x.dt.total_seconds()
)

# Compute the correlation matrix
corr = df_garmin_days.corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=np.bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(
    corr,
    mask=mask,
    cmap=cmap,
    vmax=0.3,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
)

plt.show()

corr.style.background_gradient(cmap="coolwarm")
