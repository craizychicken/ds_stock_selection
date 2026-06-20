import sql_init
import pandas as pd
import yfinance as yf
from datetime import date

DB_NAME = "asx_stock_data"
TICKER_TB = "ticker_list"
file_path = "sql_login.json"
ticker_path = "ticker.csv"

def download_ticker(ticker, start = None):
    """Downloads 2 year past data, and parse the data
       Unless specified the start date

    Args:
        ticker (str): ticker symbol

    Returns:
        pandas df of stock data
    """
    if start is None:
        data = yf.download(ticker, period="2y")
    else:
        data = yf.download(ticker, start=start, end=date.today())
    data.columns=data.columns.droplevel("Ticker")
    data.columns.name = None
    data.drop(columns=["Open"], inplace=True)
    return data

def trailing_return(df, month=12):
    """Calculate a n-month trailing momentum for every ticker

    Args:
        df (Pandas df)
        month (int):. Defaults to 12.
    """
    df["momentum"] = (df
                      .groupby("symbol")["close"]
                      .transform(lambda x: x / x.shift(month*21) - 1))
    
    return df

# Run me initially to put in ticker list from csv to db sql
# And create initalise the stock data table
if __name__ == "__main__":
    connection, mycursor = sql_init.connect_to_mysql(file_path, DB_NAME)
    df = pd.read_csv(ticker_path)
    t_list = df["Ticker"].to_list()
    sql_init.create_ticker_table(mycursor)

    # Start of Transaction
    sql_init.insert_ticker(mycursor, t_list)
    connection.commit()
    # End of Transaction

    sql_init.create_stock_table(mycursor)
    sql_init.close_connection(connection)