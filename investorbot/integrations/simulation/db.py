import time
from investorbot import crypto_service
from investorbot.integrations.simulation import simulation_db_service
from investorbot.integrations.simulation.models import PositionBalanceSimulated


def init_simulation_db():
    simulation_db_service.run_migration()

    # TODO move this to its own integration test under...
    # integration/test_integrations/test_simulations/test_services.py
    initial_wallet = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )
    initial_wallet_two = PositionBalanceSimulated(
        coin_name="USD", market_value=110.0, quantity=110.0, reserved_quantity=0.0
    )
    initial_wallet_three = PositionBalanceSimulated(
        coin_name="USD", market_value=120.0, quantity=120.0, reserved_quantity=0.0
    )

    simulation_db_service.add_item(initial_wallet)
    time.sleep(2)
    simulation_db_service.add_item(initial_wallet_two)
    time.sleep(2)
    simulation_db_service.add_item(initial_wallet_three)

    result = crypto_service.get_coin_balance("USD")
    print(result)
