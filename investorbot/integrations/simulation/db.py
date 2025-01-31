from investorbot.context import bot_context
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.integrations.simulation.services import SimulatedCryptoService


def init_simulation_db():
    crypto_service = bot_context.crypto_service

    if isinstance(crypto_service, SimulatedCryptoService):

        crypto_service.simulation_db.run_migration()

        initial_wallet = PositionBalanceSimulated(
            coin_name="USD", quantity=100.0, reserved_quantity=0.0
        )

        crypto_service.simulation_db.add_item(initial_wallet)
    else:
        raise NotImplementedError(
            "Unexpected service passed to database initialization for simulation."
        )
