from investorbot.config import config
from investorbot.interfaces.providers import ITimeProvider
from investorbot.providers import TimeProvider


def is_simulation() -> bool:
    return config.is_simulation


def is_crypto_dot_com() -> bool:
    return config.is_crypto_dot_com


# Module-level time provider for backward compatibility.
# Uses config to determine which provider to use.
if config.is_simulation:
    from investorbot.integrations.simulation.providers import SimulatedTimeProvider

    time: ITimeProvider = SimulatedTimeProvider()
else:
    time: ITimeProvider = TimeProvider()
