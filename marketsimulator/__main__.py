import argh
from marketsimulator.db import init_db
from marketsimulator.websocket import run_websocket

if __name__ == "__main__":
    argh.dispatch_commands([init_db, run_websocket])
