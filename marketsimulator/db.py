from marketsimulator import market_simulator_service


def init_db():
    market_simulator_service.run_migration()
