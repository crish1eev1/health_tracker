# -----------------------------------------------------------------------------
# SCRIPT EXTRACT_DATA.PY DESCRIPTION
# Input: Garmin SQLite Databases paths (after executing cd .\venv\Scripts\ then  py garmindb_cli.py --all --download --import --analyze --latest)
# Output: Pickle and CSV files of potentially useful tables (data/raw)
# -----------------------------------------------------------------------------
import pandas as pd

import sqlite3
import os

from utils import print_database_tables

# -----------------------------------------------------------------------------
# Defining databases paths
# -----------------------------------------------------------------------------
# Path variables to databases
db_garmin = "C:\\Users\\33671\\HealthData\\DBs\\garmin.db"
db_garmin_activities = "C:\\Users\\33671\\HealthData\\DBs\\garmin_activities.db"
db_garmin_monitoring = "C:\\Users\\33671\\HealthData\\DBs\\garmin_monitoring.db"
db_garmin_summary = "C:\\Users\\33671\\HealthData\\DBs\\garmin_summary.db"
db_summary = "C:\\Users\\33671\\HealthData\\DBs\\summary.db"

# List of database paths
database_paths = [
    db_garmin,
    db_garmin_activities,
    db_garmin_monitoring,
    db_garmin_summary,
    db_summary,
]
# -----------------------------------------------------------------------------
# Inspecting databases to return table names and, optionally, row counts
# -----------------------------------------------------------------------------
print("\n_____Inspecting databases_____")


def get_tables_from_dbs(database_paths: list, row_count: bool = False) -> dict:
    """Returns a dictionary with database names as keys and all tables contained in that database as values.

    Args:
        database_paths (list): A list of database paths.
        row_count (bool): If True, includes the row count of each table in the returned dictionary. Default is False.

    Returns:
        dict: A dictionary with database names as keys and lists of table names as values. If row_count is True, the lists will include tuples with the table name and row count.
    """
    tables_by_name = {}
    for database_path in database_paths:
        # Extract the file name from the file path
        database_name = os.path.basename(database_path)

        # Connect to the database
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            # Extract the table names from the results of the SELECT query
            table_names = [row[0] for row in cursor.fetchall()]
            if row_count:
                # Include the row count in the table names list
                table_names = [
                    (name, cursor.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
                    for name in table_names
                ]
            # Add the database name and table names to the dictionary
            tables_by_name[database_name] = table_names

    return tables_by_name


db_tables = get_tables_from_dbs(database_paths, row_count=True)

# Printing results in a clear and readable way
# -----------------------------------------------------------------------------
print_database_tables(db_tables, title="Initial Databases Tables:")
# Count the number of databases
num_databases = len(db_tables)
# Initialize a variable to store the total number of tables
num_tables = 0
# Iterate over the dictionary
for database, tables in db_tables.items():
    # Add the number of tables in this database to the total number of tables
    num_tables += len(tables)
# Print the number of databases and tables
print(f"Number of databases: {num_databases}")
print(f"Number of tables: {num_tables}")

# -----------------------------------------------------------------------------
# Removing empty tables from the list of interesting tables to look at
# -----------------------------------------------------------------------------
print("\n_____Removing empty tables_____")


def remove_empty_tables(tables_by_name: dict) -> dict:
    """Returns a copy of the input dictionary with all tables that have 0 rows removed.

    Args:
        tables_by_name (dict): A dictionary with database names as keys and lists of table names as values.

    Returns:
        dict: A copy of the input dictionary with empty tables removed.
    """
    return {
        database: [(name, count) for name, count in tables if count > 0]
        for database, tables in tables_by_name.items()
    }


db_tables_and_rows_non_null = remove_empty_tables(db_tables)

# Printing results in a clear and readable way
# -----------------------------------------------------------------------------
print_database_tables(db_tables_and_rows_non_null, title="Tables kept:")
# Count the number of databases
num_databases = len(db_tables_and_rows_non_null)
# Initialize a variable to store the total number of tables
num_tables = 0
# Iterate over the dictionary
for database, tables in db_tables_and_rows_non_null.items():
    # Add the number of tables in this database to the total number of tables
    num_tables += len(tables)
# Print the number of databases and tables
print(f"Number of databases: {num_databases}")
print(f"Number of tables: {num_tables}")


# -----------------------------------------------------------------------------
# Keeping a selected list of tables after manual inspection
# -----------------------------------------------------------------------------
print("\n_____Keeping a selection of tables to work with_____")

# Reformat
db_tables_reformatted = {
    database: {table: rows_count for table, rows_count in tables}
    for database, tables in db_tables_and_rows_non_null.items()
}

# To keep
keys_to_keep = {
    "garmin.db": ["stress", "sleep", "daily_summary"],
    "garmin_activities.db": [
        "activities",
        "activity_laps",
        "activity_records",
        "steps_activities",
    ],
    "garmin_monitoring.db": ["monitoring_hr", "monitoring_rr"],
    "garmin_summary.db": [
        "years_summary",
        "months_summary",
        "weeks_summary",
        "days_summary",
        "intensity_hr",
    ],
    "summary.db": ["years_summary", "months_summary", "weeks_summary", "days_summary"],
}


def keep_keys(dictionary, keys_to_keep):
    result = {}
    for outer_key, inner_dict in dictionary.items():
        if outer_key in keys_to_keep:
            inner_keys = list(inner_dict.keys())
            result[outer_key] = {}
            for inner_key in inner_keys:
                if inner_key in keys_to_keep[outer_key]:
                    result[outer_key][inner_key] = inner_dict[inner_key]
    return result


tables_to_keep = keep_keys(db_tables_reformatted, keys_to_keep)


# Printing results in a clear and readable way
# Count the number of databases
num_databases = len(tables_to_keep)
# Initialize a variable to store the total number of tables
num_tables = 0
# Iterating over the keys and values in the dictionary and print them using indented blocks.
print("Tables kept:")
for database, tables in tables_to_keep.items():
    num_tables += len(tables)
    print(f"{database}:")
    for table, rows_count in tables.items():
        print(f" - {table}: {rows_count}")
print("\n")
# Print the number of databases and tables
print(f"Number of databases: {num_databases}")
print(f"Number of tables: {num_tables}")

# -----------------------------------------------------------------------------
# Querying the selection of dataframe we're interested in
# -----------------------------------------------------------------------------
print("\n_____Querying the selected dataframes_____")


def get_dataframes(databases):
    """Returns a dictionary of Pandas dataframes for the specified tables in the SQLite databases.

    Parameters:
    databases (dict): A dictionary that specifies which tables to retrieve data from in each database. The keys of the dictionary should be the paths to the databases, and the values should be lists of the names of the tables to include in the dataframe.

    Returns:
    dict: A dictionary of Pandas dataframes, one for each table in each database. The keys of the dictionary will be the names of the tables, and the values will be the corresponding dataframes.
    """
    dataframes = {}
    for db_path, tables in databases.items():
        database_name = os.path.basename(db_path)
        # Connect to the database
        conn = sqlite3.connect(db_path)
        for table_name in tables:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
            dataframes[database_name + "_" + table_name] = df
        # Close the connection
        conn.close()
    return dataframes


# Specify the databases and tables to retrieve
databases = {
    f"{db_garmin}": ["stress", "sleep", "daily_summary"],
    f"{db_garmin_activities}": [
        "activities",
        "activity_laps",
        "activity_records",
        "steps_activities",
    ],
    f"{db_garmin_monitoring}": ["monitoring_hr", "monitoring_rr"],
    f"{db_garmin_summary}": [
        "years_summary",
        "months_summary",
        "weeks_summary",
        "days_summary",
        "intensity_hr",
    ],
    f"{db_summary}": [
        "years_summary",
        "months_summary",
        "weeks_summary",
        "days_summary",
    ],
}

# Get the dataframes
dataframes = get_dataframes(databases)

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
# Export the results
# -----------------------------------------------------------------------------
print("\n_____Exporting the results_____")

for key, df in dataframes.items():
    # Save the dataframe as a pickle file
    df.to_pickle(f"../../data/raw/{key}.pkl")
    # Save the dataframe as a CSV file
    df.to_csv(f"../../data/raw/{key}.csv")

print(f"Tables exported: {len(dataframes)}")
print(f"Total rows: {total_rows}")
print(f"Total columns: {total_columns}")
# -----------------------------------------------------------------------------
# download all data and create db by:
# garmindb_cli.py --all --download --import --analyze

# Incrementally update db:
# garmindb_cli.py --all --download --import --analyze --latest

# backup DB files occasionally:
# garmin_cli.py --backup
# -----------------------------------------------------------------------------
