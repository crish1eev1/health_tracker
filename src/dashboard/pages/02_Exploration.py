# -----------------------------------------------------------------------------
# streamlit run your_script.py
# -----------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

import os
from datetime import datetime
from PIL import Image

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
df_garmin_monitoring = dataframes["garmin_monitoring"]
df_garmin_monitoring_resampled = dataframes["garmin_monitoring_resampled"]
df_garmin_days = dataframes["garmin_days"]


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
