from calculator import *
from oks_api import *

SYMBOL = "BTC-USDT"
BUY_CURRENCY = "USDT"
SELL_CURRENCY = "BTC"
TEMA_BAR = "1D"  # TEMA on daily period
ALLIGATOR_BAR = "1H"  # Williams Alligator on hourly period
INTERVAL = 3600  # Every hour for 1-hour interval checks
LIMIT = 100
ZERO_THRESHOLD = 10  # Threshold for determining proximity to 0
SECOND_DERIVATIVE_THRESHOLD = 1  # Threshold for second derivative reasonable range
LOSS_THRESHOLD = -3  # 3% loss threshold for risk management


def main():
    last_operation = 0  # Track the last operation, initially 0 (no action)
    capital = 10000  # Initial capital, for example

    while True:
        start_time = time.time()

        # Fetch daily TEMA data and 1-hour Alligator data
        df_tema = get_market_data(SYMBOL, TEMA_BAR, LIMIT)
        df_alligator = get_market_data(SYMBOL, ALLIGATOR_BAR, LIMIT)

        # Calculate TEMA signals on a daily timeframe
        calculate_tema_signal(df_tema, ZERO_THRESHOLD, SECOND_DERIVATIVE_THRESHOLD)

        # Calculate Alligator signals on an hourly timeframe
        calculate_alligator_signal(df_alligator)

        # Determine trading decision
        operation = df_tema.tail(1)['Signal'].values[0]

        # Apply risk management - Cut loss if the position has a loss > LOSS_THRESHOLD
        if capital < capital * (1 + LOSS_THRESHOLD / 100):
            full_sell(SYMBOL, SELL_CURRENCY)
            last_operation = 0  # Reset operation
            print("Loss cut applied. Recalibrating position...")
            continue

        # Trade based on TEMA and Alligator signals
        if operation == 1 and last_operation != 1:
            # Buy if TEMA signal is positive and last operation wasn't a buy
            full_buy(SYMBOL, BUY_CURRENCY)
            last_operation = 1
            print("Buy executed.")
        elif operation == -1 and last_operation != -1:
            # Sell if TEMA signal is negative and last operation wasn't a sell
            full_sell(SYMBOL, SELL_CURRENCY)
            last_operation = -1
            print("Sell executed.")
