from investorbot.constants import INVESTOR_APP_INTEGRATION
from investorbot.enums import AppIntegration
from investorbot.integrations.simulation.providers import SimulatedTimeProvider
from investorbot.interfaces.providers import ITimeProvider
from investorbot.providers import TimeProvider


def is_simulation() -> bool:
    return INVESTOR_APP_INTEGRATION == AppIntegration.SIMULATED


def is_crypto_dot_com() -> bool:
    return INVESTOR_APP_INTEGRATION == AppIntegration.CRYPTODOTCOM


time: ITimeProvider = SimulatedTimeProvider() if is_simulation() else TimeProvider()
