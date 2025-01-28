from investorbot.integrations.simulation.constants import SIMULATION_DB_CONNECTION
from investorbot.integrations.simulation.interfaces import ITime
from investorbot.integrations.simulation.services import SimulationService, TestingTime


simulation_db_service = SimulationService(SIMULATION_DB_CONNECTION)

# TODO placeholder for when time implementation gets more complex.
time_service: ITime = TestingTime()
