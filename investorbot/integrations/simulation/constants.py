from investorbot.config import config

SIMULATION_DB_PATH = f"{config.app_path}simulation.db"
SIMULATION_DB_CONNECTION = f"sqlite:///{SIMULATION_DB_PATH}"
TIME_SERIES_DATA_PATH = f"{config.app_path}/simulation.csv"
