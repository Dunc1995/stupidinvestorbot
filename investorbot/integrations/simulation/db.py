from investorbot.integrations.simulation import simulation_db_service
from investorbot.integrations.simulation.models import PositionBalanceSimulated


def init_simulation_db():
    simulation_db_service.run_migration()

    initial_wallet = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )

    simulation_db_service.add_item(initial_wallet)
