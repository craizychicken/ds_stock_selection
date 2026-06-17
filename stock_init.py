import sql_init
import pandas as pd
import yfinance as yf

DB_NAME = "asx_stock_data"
TICKER_TB = "ticker_list"
file_path = "sql_login.json"
ticker_path = "ticker.csv"

def download_ticker(ticker):
    """Downloads 2 year past data, and parse the data

    Args:
        ticker (str): ticker symbol

    Returns:
        pandas df of stock data
    """
    data = yf.download(ticker, period="2y")
    data.columns=data.columns.droplevel("Ticker")
    data.columns.name = None
    data.drop(columns=["Open"])
    return data


# Run me initially to put in ticker list from csv to db sql
if __name__ == "__main__":
    mydb, mycursor = sql_init.connect_to_mysql(file_path, DB_NAME)
    df = pd.read_csv(ticker_path)
    t_list = df["Ticker"].to_list()
    sql_init.create_ticker_table(mycursor)
    # Start of Transaction
    sql_init.insert_ticker(mycursor, t_list)
    mydb.commit()
    # End of Transaction
    sql_init.close_connection(mydb)