from chalicelib.models.app import CoinSummary, TradingStatus


class CoinSelection:

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
        experiences high gain.

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
    def all_guns_blazing(summary: CoinSummary) -> bool:
        return (
            summary.percentage_change_24h > 0.20 and summary.percentage_std_24h > 0.05
        )

    @staticmethod
    def should_select_coin(summary: CoinSummary, strategy: str):
        select_coin = False

        match strategy:
            case "high_gain":
                select_coin = CoinSelection.high_gain(summary)
            case "conservative":
                select_coin = CoinSelection.conservative(summary)
            case "all_guns_blazing":
                select_coin = CoinSelection.all_guns_blazing(summary)
            case _:
                select_coin = False

        return select_coin


class SellPrice:
    @staticmethod
    def get_percentage_increase(status: TradingStatus):
        percentage_increase = None

        match status.sell_strategy:
            case "high_gain":
                percentage_increase = 1.01
            case "conservative":
                percentage_increase = 1.01
            case "all_guns_blazing":
                percentage_increase = 0.9
            case _:
                percentage_increase = 1.01

        return percentage_increase
