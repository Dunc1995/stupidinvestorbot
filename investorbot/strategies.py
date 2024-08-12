from enum import Enum
from investorbot.structs.internal import CoinSummary


class CoinSelectionStrategies(Enum):
    CONSERVATIVE = "conservative"
    HIGH_GAIN = "high_gain"
    ALL_GUNS_BLAZING = "all_guns_blazing"

    @staticmethod
    def conservative(summary: CoinSummary) -> bool:
        """Selects a coin that has near 0% change in the last 24 hours,
        but with high volatility (standard deviation).

        Args:
            summary (CoinSummary): Coin data to analyse.

        Returns:
            bool: True if the coin is volatile but with 0% change in the most recent trade.
        """
        return summary.has_high_std and summary.has_low_change

    @staticmethod
    def high_gain(summary: CoinSummary) -> bool:
        """Selects a coin that is within its standard 24h deviation but
        experiences high gain. Empirically this selection criteria tends
        to yield decent returns.

        Args:
            summary (CoinSummary): Coin data to analyse.

        Returns:
            bool: True if the coin is within standard deviation.
        """
        mean = float(summary.mean_24h)
        std = float(summary.std_24h)
        return (
            bool(float(summary.latest_trade) - (mean + std) <= 0)
            and summary.percentage_std_24h > 0.03
        )

    @staticmethod
    def all_guns_blazing(
        summary: CoinSummary,
    ) -> bool:  # ! This is almost certainly stupid.
        return (
            summary.percentage_change_24h > 0.20 and summary.percentage_std_24h > 0.05
        )


# class SellPrice:
#     @staticmethod
#     def get_percentage_increase(status: TradingStatus):
#         percentage_increase = None

#         match status.sell_strategy:
#             case CoinSelectionStrategies.HIGH_GAIN:
#                 percentage_increase = 1.01
#             case CoinSelectionStrategies.CONSERVATIVE:
#                 percentage_increase = 1.01
#             case CoinSelectionStrategies.ALL_GUNS_BLAZING:
#                 percentage_increase = 0.9
#             case _:
#                 percentage_increase = 1.01

#         return percentage_increase
