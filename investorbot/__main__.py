import argh
from investorbot.routines import buy_coin_routine, init_db, sell_coin_routine

if __name__ == "__main__":
    argh.dispatch_commands([buy_coin_routine, sell_coin_routine, init_db])
