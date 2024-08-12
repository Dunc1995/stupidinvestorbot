import pandas as pd
import datetime as dt

from investorbot.structs.internal import TimeSeriesSummary


def get_coin_time_series_summary(time_series_data: dict) -> TimeSeriesSummary:
    """Fetches time-series data for the coin of interest and summarizes basic statistical properties via
    the CoinSummary object. Used for determining which coins to invest in.

    Args:
        coin (Ticker): Object obtained via API call to Crypto.com API.

    Returns:
        CoinSummary: data container for coin statistics.
    """
    df = pd.DataFrame.from_dict(time_series_data)
    df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
    df["v"] = df["v"].astype(float)

    stats = df
    mean = stats["v"].mean()
    std = stats["v"].std()
    modes = stats["v"].mode()
    percentage_std = float(std) / float(mean)

    return TimeSeriesSummary(
        mean=mean,
        modes=modes,
        std=std,
        percentage_std=percentage_std,
    )
