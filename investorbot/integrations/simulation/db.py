from investorbot.integrations.simulation import simulation_service


def init_simulation_db():
    simulation_service.run_migration()
