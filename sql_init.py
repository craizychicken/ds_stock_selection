import mysql.connector
import json

def create_database(mycursor, db_name):
    # Create database if it doesn't exist
    mycursor.execute(f"CREATE DATABASE {db_name}")
    return

def check_database_exists(mycursor, db_name):
    """Executes the code:
        SHOW DATABASES
        and checks if the database name is in the list of databases.

    Returns:
        Bool: True if database exists, False otherwise.
    """
    mycursor.execute("SHOW DATABASES")
    # Fetch all results, results are small so fetch all
    databases = mycursor.fetchall()
    # Checking if exists
    return db_name in [db[0] for db in databases]

def connect_to_mysql(file_path, db_name):
    """Connects to Local MySQL server
        if the database doesn't exist, it will be created.
        if the connection fails, None is returned.

    Args:
        file_path: string path to json with login details

    Returns:
        None: if connection fails, otherwise the connection object.
    """
    with open(file_path, "r") as f:
        login_info = json.load(f)
    try:
        connection = mysql.connector.connect(
            host=login_info["host"],
            user=login_info["user"],
            password=login_info["password"]
        )

        mycursor = connection.cursor()
        if not check_database_exists(mycursor, db_name):
            create_database(mycursor, db_name)
    except mysql.connector.Error:
        return None
    mycursor.execute(f"USE {db_name}")
    return connection, mycursor

def check_table_exists(mycursor, tb_name):
    """Executes the code:
        SHOW TABLES
        and checks if the table name is in the list of tables.

    Returns:
        Bool: True if table exists, False otherwise.
    """
    mycursor.execute("SHOW TABLES")
    # Fetch all results, results are small so fetch all
    tables = mycursor.fetchall()
    # Checking if exists
    return tb_name in [tb[0] for tb in tables]

def create_ticker_table(mycursor):
    """Creates a table specifically for the ticker
    """
    if check_table_exists(mycursor, "ticker_list"):
        return
    create_query = """CREATE TABLE ticker_list(
                        symbol  VARCHAR(4)  NOT NULL,
                        PRIMARY KEY (symbol))"""
    mycursor.execute(create_query)
    return

def insert_ticker(mycursor, ticker_list):
    for ticker in ticker_list:
        query = f"""INSERT INTO ticker_list VALUES
                        (%s)
                """
        mycursor.execute(query, (ticker,))
    return

def create_stock_table(mycursor):
    """Creates a table for a stock
    """
    if check_table_exists(mycursor, "stock_data"):
        return
    create_query = """CREATE TABLE stock_data(
                        symbol VARCHAR(4),
                        date DATE,
                        close DECIMAL(10, 2),
                        high DECIMAL(10, 2),
                        low DECIMAL(10, 2),
                        volume BIGINT,
                        PRIMARY KEY (symbol, date),
                        FOREIGN KEY (symbol) REFERENCES ticker_list(symbol))"""
    mycursor.execute(create_query)
    return

def insert_stock_data(mycursor, ticker, df):
    """
    Insert data from parsed csv to our stock data table
    """
    df = df.reset_index()
    df["Date"] = df["Date"].dt.date

    rows = [
        (
            ticker,
            row.Date,
            row.Close,
            row.High,
            row.Low,
            row.Volume
        )
        for row in df.itertuples(index=False)
    ]
    query = """
        INSERT INTO stock_data
        (symbol, date, close, high, low, volume)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

    mycursor.executemany(query, rows)
    return

def close_connection(connection):
    # Close connection
    connection.close()