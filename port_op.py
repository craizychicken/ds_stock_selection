from pypfopt import EfficientFrontier, risk_models, expected_returns
import pandas as pd

def equal_w(symbols):
    w = 1/len(symbols)
    return {symbol:w for symbol in symbols}

def mpt_w(symbols, mycursor):
    placeholders = ",".join(["%s"] * len(symbols))

    query = f"""
        SELECT symbol, date, log_return
        FROM signals
        WHERE symbol IN ({placeholders})
    """
    mycursor.execute(query, symbols)

    df = pd.DataFrame(mycursor.fetchall())
    df.columns = ["symbol", "date", "log_return"]

if __name__ == "__main__":
    import sql_init
    connection, mycursor = sql_init.connect_to_mysql("sql_login.json", "asx_stock_data")
    print(mpt_w(["CSL"],  mycursor))
    sql_init.close_connection(connection)


