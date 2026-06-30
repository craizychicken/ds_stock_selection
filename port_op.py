from pypfopt import EfficientFrontier, expected_returns
from pandas import DataFrame, Series
import numpy as np
import ctypes

file = "C:\\Users\\benke\\OneDrive\\Documents\\Project\\quant\\covariance.dll"
RFR = 0.047

def equal_w(symbols):
    w = 1/len(symbols)
    return {symbol:w for symbol in symbols}

def calculateCovMatrix(data: DataFrame):
    """
    Uses C++ to calculate Covariance Matrix

    data: The prices data
    """
    lib = ctypes.CDLL(file)

    func = lib.calculateCovMatrix
    # Defining the function
    func.argtypes = [
        ctypes.POINTER(ctypes.c_double), # Data
        ctypes.c_int,                    # n Cols
        ctypes.c_int,                    # n Rows
        ctypes.POINTER(ctypes.c_double)  # Output.
    ]
    func.restype = None

    columns = data.columns.rename(None) # Stock names

    # Get the args
    data = data.to_numpy(dtype=np.double)
    rows,cols = data.shape
    out = np.zeros((cols,cols), dtype=np.double)

    func(data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
         rows,
         cols,
         out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))

    return DataFrame(out, index=columns, columns=columns)

def mpt_w(return_df: DataFrame, cov_matrix: DataFrame):
    """Gets the optimal weightings based on MPT

    Args:
        return_df (pd.DataFrame): df with symbol, date, log_return
        price_df (pd.DataFrame): df with symbol, date, close
    """
    # Get anualised returns
    df = return_df.pivot(index="date", columns="symbol", values="log_return")
    mu = expected_returns.mean_historical_return(df, returns_data=True, frequency=252)

    # Find Weights based on best sharpe ratio given RFR
    ef = EfficientFrontier(mu, cov_matrix, weight_bounds=(0.05, 0.2))
    ef.max_sharpe(risk_free_rate=RFR)
    return ef.clean_weights(cutoff=0.001, rounding=4)

def inv_vol(vol_list: Series):
    return (1/vol_list)/(1/vol_list).sum()

def recent_cross(signal: DataFrame, window: int):
    df = signal.copy()
    # shift to get yesterday's values
    df['prev_ma50']  = df.groupby('symbol')['ma_50'].shift(1)
    df['prev_ma200'] = df.groupby('symbol')['ma_200'].shift(1)

    # golden cross - 50 flips above 200
    df['golden_cross'] = (
        (df['prev_ma50']  <= df['prev_ma200']) &
        (df['ma_50'] > df['ma_200'])
    )

    # death cross - 50 flips below 200
    df['death_cross'] = (
        (df['prev_ma50']  >= df['prev_ma200']) &
        (df['ma_50'] < df['ma_200'])
    )
    df["cross"] = df["golden_cross"].astype(int) - df["death_cross"].astype(int)
    df['cross_nz'] = df['cross'].where(df['cross'] != 0)
    df['cross_ffill'] = df.groupby('symbol')['cross_nz'].transform(
        lambda x: x.ffill(limit=window)
    )

    return (df["cross_ffill"].fillna(0) + 1)/2

def pick_stocks(signal_df: DataFrame, date, 
                sig_w = {"momentum": 0.4, "z_momentum": 0.3,
                         "cross": 0.3},
                n=10):
    """Picks the Top 10 ideal stocks for a current month
        Based on the Signals
    """
    df = signal_df.copy()
    df["recent_cross"] = recent_cross(df[["symbol","ma_50", "ma_200"]], 20)
    df["z_mom_rank"] = df.groupby("date")["z_momentum"].rank(pct=True)

    #Filter df for only the current date
    df = df[df["date"] == date]
    df = df[df["z_momentum"].abs() <= 2] # Remove potential bubbles
    
    # step 3 - weighted composite
    df['composite'] = (
        sig_w["momentum"]   * df['mom_rank'] +
        sig_w["z_momentum"] * df['z_mom_rank'] +
        sig_w["cross"]      * df['recent_cross']
    )

    return df.sort_values("composite", ascending=False).head(n)["symbol"]