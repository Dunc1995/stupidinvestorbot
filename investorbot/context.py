"""Application context and dependency wiring.

BotContext is the composition root for the application. It can be constructed with explicit
dependencies (for testing and flexibility) or will lazily create defaults based on environment
configuration.
"""

from dataclasses import dataclass
import logging
from typing import Optional

from investorbot.config import config, DEFAULT_LOGS_NAME
from investorbot.enums import AppIntegration
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
    """Composition root for the investorbot application.

    Accepts explicit dependencies for testing. When dependencies are not provided, they are
    lazily created from environment configuration.
    """

    _bot_db_service: Optional[BotDbService] = None
    _crypto_service: Optional[ICryptoService] = None
    _smtp_service: Optional[SmtpService] = None

    @property
    def db_service(self) -> BotDbService:
        """The investorbot application's database service layer."""
        if self._bot_db_service is not None:
            return self._bot_db_service

        self._bot_db_service = BotDbService(config.db_connection)
        return self._bot_db_service

    @property
    def crypto_service(self) -> ICryptoService:
        if self._crypto_service is not None:
            return self._crypto_service

        crypto_service = None

        if config.is_simulation:
            from investorbot.integrations.simulation.constants import (
                SIMULATION_DB_CONNECTION,
            )
            from investorbot.integrations.simulation.interfaces import IDataProvider
            from investorbot.integrations.simulation.providers import DataProvider
            from investorbot.integrations.simulation.services import (
                SimulatedCryptoService,
                SimulationDbService,
            )

            simulation_db_service = SimulationDbService(SIMULATION_DB_CONNECTION)
            data_provider: IDataProvider = DataProvider(2000)

            crypto_service = SimulatedCryptoService(
                simulation_db_service, data_provider
            )

            logger.info(SIMULATED_ENVIRONMENT_MESSAGE)
        elif config.is_crypto_dot_com:
            from investorbot.integrations.cryptodotcom.services import CryptoService

            crypto_service = CryptoService()
            logger.info(CRYPTO_DOT_COM_ENVIRONMENT_MESSAGE)

        elif not config.is_testing:
            raise EnvironmentError(ENVIRONMENT_ERROR_MESSAGE)

        self._crypto_service = crypto_service

        return crypto_service

    @property
    def smtp_service(self) -> SmtpService:
        if self._smtp_service is not None:
            return self._smtp_service

        self._smtp_service = SmtpService()
        return self._smtp_service


def create_default_context() -> BotContext:
    """Factory function to create a BotContext with default (environment-based) configuration."""
    return BotContext()


# Default application context. Can be replaced in tests or overridden at startup.
bot_context = create_default_context()
"""Describes available services across the investorbot application."""
