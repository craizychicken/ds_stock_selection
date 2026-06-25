from pypfopt import EfficientFrontier, risk_models, expected_returns
import pandas as pd
import numpy as np
import ctypes

file = "C:\\Users\\benke\\OneDrive\\Documents\\Project\\quant\\covariance.dll"
RFR = 0.047

def equal_w(symbols):
    w = 1/len(symbols)
    return {symbol:w for symbol in symbols}

def calculateCovMatrix(data: pd.DataFrame):
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

    return pd.DataFrame(out, index=columns, columns=columns)

#! Change me later
def mpt_w(symbols: list, return_df: pd.DataFrame, price_df: pd.DataFrame):
    """Gets the optimal weightings based on MPT

    Args:
        return_df (pd.DataFrame): df with symbol, date, log_return
        price_df (pd.DataFrame): df with symbol, date, close
    """
    # Get anualised returns
    return_df = return_df.pivot(index="date", columns="symbol", values="log_return")
    mu = expected_returns.mean_historical_return(return_df, returns_data=True, frequency=252)

    # Get Covariance matrix
    data = (
        price_df
        .sort_values("date")
        .pivot(
            index="date",
            columns="symbol",
            values="close"
        )
    )
    cov_matrix = calculateCovMatrix(data)
    # Find Weights based on best sharpe ratio given RFR
    ef = EfficientFrontier(mu, cov_matrix)
    ef.max_sharpe(risk_free_rate=RFR)
    return ef.clean_weights(cutoff=0.001, rounding=4)


