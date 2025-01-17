import argh
from marketsimulator.db import init_db
from marketsimulator.websocket import run_websocket
from marketsimulator.app import run

if __name__ == "__main__":
    argh.dispatch_commands([init_db, run_websocket, run])
