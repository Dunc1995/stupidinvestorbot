from investorbot.integrations.simulation.constants import SIMULATION_DB_CONNECTION
from investorbot.integrations.simulation.interfaces import IDataProvider, ITime
from investorbot.integrations.simulation.providers import DataProvider
from investorbot.integrations.simulation.services import SimulationService, TestingTime


# TODO placeholder for when time implementation gets more complex.
time_service: ITime = TestingTime()
simulation_db_service = SimulationService(SIMULATION_DB_CONNECTION)
data_provider: IDataProvider = DataProvider()
