from investorbot.integrations.simulation.constants import SIMULATION_DB_CONNECTION
from investorbot.integrations.simulation.interfaces import IDataProvider, ITime
from investorbot.integrations.simulation.providers import (
    DataProvider,
    SimulatedTimeProvider,
)
from investorbot.integrations.simulation.services import SimulationService


simulation_db_service = SimulationService(SIMULATION_DB_CONNECTION)

time_provider: ITime = SimulatedTimeProvider()
data_provider: IDataProvider = DataProvider(time_provider)
