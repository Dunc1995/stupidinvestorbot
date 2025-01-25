from investorbot.integrations.simulation import simulation_db_service


def init_simulation_db():
    simulation_db_service.run_migration()
