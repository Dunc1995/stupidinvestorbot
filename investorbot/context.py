from dataclasses import dataclass
import logging

from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    INVESTOR_APP_DB_CONNECTION,
    INVESTOR_APP_ENVIRONMENT,
)
from investorbot.enums import AppIntegration
from investorbot.env import is_crypto_dot_com, is_simulation
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.integrations.simulation.constants import SIMULATION_DB_CONNECTION
from investorbot.integrations.simulation.interfaces import (
    IDataProvider,
)
from investorbot.integrations.simulation.providers import (
    DataProvider,
)
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationDbService,
)
from investorbot.interfaces.services import ICryptoService
from investorbot.services import BotDbService, SmtpService

logger = logging.getLogger(DEFAULT_LOGS_NAME)


SIMULATED_ENVIRONMENT_MESSAGE = """
Using simulated crypto service. This ensures the application is entirely self-contained and can be
used for devising the best trading strategy. Use this service to ascertain a long-term strategy.
"""

CRYPTO_DOT_COM_ENVIRONMENT_MESSAGE = """
Connected to the Crypto.com API. The investorbot application was initially developed in conjunction
with this API. Fees are allegedly high/hidden on this trading platform so eventually the bot should
be moved to another platform.
"""

ENVIRONMENT_ERROR_MESSAGE = f"""
Please specify a trading platform integration via environment variable. For example:

`export INVESTOR_APP_INTEGRATION=SIMULATED`

Your options are {list(str(option) for option in AppIntegration)}
"""


@dataclass
class BotContext:
    __bot_db_service: BotDbService = None
    __crypto_service: ICryptoService = None
    __smtp_service: SmtpService = None

    @property
    def db_service(self) -> BotDbService:
        """The investorbot application's database service layer."""

        return (
            self.__bot_db_service
            if self.__bot_db_service is not None
            else BotDbService(INVESTOR_APP_DB_CONNECTION)
        )

    @property
    def crypto_service(self) -> ICryptoService:
        if self.__crypto_service is not None:
            return self.__crypto_service

        crypto_service = None

        if is_simulation():
            simulation_db_service = SimulationDbService(SIMULATION_DB_CONNECTION)
            data_provider: IDataProvider = DataProvider()

            crypto_service = SimulatedCryptoService(
                simulation_db_service, data_provider
            )

            logger.info(SIMULATED_ENVIRONMENT_MESSAGE)
        elif is_crypto_dot_com():
            crypto_service = CryptoService()
            logger.info(CRYPTO_DOT_COM_ENVIRONMENT_MESSAGE)

        elif INVESTOR_APP_ENVIRONMENT != "Testing":
            raise EnvironmentError(ENVIRONMENT_ERROR_MESSAGE)

        self.__crypto_service = crypto_service

        return crypto_service

    @property
    def smtp_service(self):
        return self.__smtp_service if self.__smtp_service is not None else SmtpService()


bot_context = BotContext()
"""Describes available services across the investorbot application."""
