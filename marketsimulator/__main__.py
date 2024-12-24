import argh
from marketsimulator.db import init_db

if __name__ == "__main__":
    argh.dispatch_commands([init_db])
