def print_database_tables(database_tables: dict, title: str) -> None:
    """Prints the names of databases and tables in a clear and readable way.

    Args:
        database_tables (dict): A dictionary with database names as keys and lists of table names as values.
    """
    # Iterating over the keys and values in the dictionary and print them using indented blocks.
    print(title)
    for database, tables in database_tables.items():
        print(f"{database}:")
        # Using if statement to check the type of the values in the dictionary and adjust the formatting accordingly.
        if isinstance(tables[0], list):
            # The values in the dictionary are lists of lists
            for table in tables:
                print(f"  - {table[0]}: {table[1]}")
        else:
            # The values in the dictionary are lists of strings
            for table in tables:
                print(f"  - {table}")
    print("\n")
