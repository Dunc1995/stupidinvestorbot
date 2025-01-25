import logging
from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    INVESTOR_APP_INTEGRATION,
    INVESTOR_APP_DB_CONNECTION,
)
from investorbot.enums import AppIntegration
from investorbot.interfaces.services import ICryptoService
from investorbot.services import AppService, SmtpService
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.integrations.simulation.services import SimulatedCryptoService

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

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def get_crypto_service(app_service: AppService) -> ICryptoService:
    __crypto_service: ICryptoService = None

    if INVESTOR_APP_INTEGRATION == AppIntegration.SIMULATED.value:
        __crypto_service = SimulatedCryptoService(app_service)
        logger.info(SIMULATED_ENVIRONMENT_MESSAGE)
    elif INVESTOR_APP_INTEGRATION == AppIntegration.CRYPTODOTCOM.value:
        __crypto_service = CryptoService()
        logger.info(CRYPTO_DOT_COM_ENVIRONMENT_MESSAGE)
    else:
        raise EnvironmentError(ENVIRONMENT_ERROR_MESSAGE)

    return __crypto_service


smtp_service = SmtpService()

app_service = AppService(INVESTOR_APP_DB_CONNECTION)
crypto_service: ICryptoService = get_crypto_service(app_service)
