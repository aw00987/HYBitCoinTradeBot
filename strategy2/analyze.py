import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from calculator import *

from oks_api import *

# Configuration Constants
SYMBOL = "BTC-USDT"
TEMA_BAR = "1H"
LIMIT = 200
EPSILON = 0.01  # Threshold for filtering noise

# Trading Bot Class
class TradingBot:
    def __init__(self, symbol, tema_bar, limit):
        self.symbol = symbol
        self.tema_bar = tema_bar
        self.limit = limit
        self.current_position = 'None'
        self.df_tema = None
        self.entry_price = None
        self.current_balance = 0
        self.current_units = 0

    def get_data(self):
        try:
            df_tema = get_market_data(self.symbol, self.tema_bar, self.limit)
            self.calculate_tema_signal(df_tema)

            filter_same_signal(df_tema)
            filter_frequent_signal(df_tema)
            filter_same_signal(df_tema)

            df_tema['timestamp'] = pd.to_datetime(pd.to_numeric(df_tema['timestamp']), unit='ms')
            self.df_tema = df_tema
            return df_tema
        except Exception as e:
            print(f"Error in fetching data: {e}")
            return None

    @staticmethod
    def calculate_tema_signal(df):
        # Calculate TEMA
        ema1 = df["close"].ewm(span=20, adjust=False).mean()
        ema2 = ema1.ewm(span=20, adjust=False).mean()
        ema3 = ema2.ewm(span=20, adjust=False).mean()
        df["TEMA"] = 3 * ema1 - 3 * ema2 + ema3

        # Calculate Slope of TEMA
        df['Slope_TEMA'] = df['TEMA'] - df['TEMA'].shift(1)

        # Initialize Signal and Position columns
        df['Signal'] = 0
        df['Position'] = 'None'

        # Decision-Making Logic Based on Slope of TEMA
        # Buy or Cover
        df.loc[
            (df['Slope_TEMA'].shift(1) <= 0) & (df['Slope_TEMA'] > 0) & (abs(df['Slope_TEMA']) > EPSILON),
            ['Signal', 'Position']
        ] = [1, 'Long']  # Buy Signal

        df.loc[
            (df['Slope_TEMA'].shift(1) < 0) & (df['Slope_TEMA'] == 0) & (abs(df['Slope_TEMA']) > EPSILON),
            ['Signal', 'Position']
        ] = [1, 'Cover']  # Cover Signal

        # Sell or Short
        df.loc[
            (df['Slope_TEMA'].shift(1) > 0) & (df['Slope_TEMA'] == 0) & (abs(df['Slope_TEMA']) > EPSILON),
            ['Signal', 'Position']
        ] = [-1, 'Sell']  # Sell Signal

        df.loc[
            (df['Slope_TEMA'].shift(1) >= 0) & (df['Slope_TEMA'] < 0) & (abs(df['Slope_TEMA']) > EPSILON),
            ['Signal', 'Position']
        ] = [-1, 'Short']  # Short Signal

        return df

    def execute_trade_sequence(self):
        for index, row in self.df_tema.iterrows():
            if row['Position'] == 'Long' and self.current_position == 'None':
                print(f"Entering long position at {row['timestamp']} with price {row['close']}")
                self.current_position = 'Long'
                self.entry_price = row['close']
                self.current_units = self.current_balance / row['close']
                # Execute buy logic here (API call)

            elif row['Position'] == 'Cover' and self.current_position == 'Short':
                print(f"Covering short position at {row['timestamp']} with price {row['close']}")
                self.current_position = 'None'
                self.entry_price = None
                # Execute cover logic here (API call)

            elif row['Position'] == 'Short' and self.current_position == 'None':
                print(f"Entering short position at {row['timestamp']} with price {row['close']}")
                self.current_position = 'Short'
                self.entry_price = row['close']
                self.current_units = self.current_balance / row['close']
                # Execute short sell logic here (API call)

            elif row['Position'] == 'Sell' and self.current_position == 'Long':
                print(f"Exiting long position and selling at {row['timestamp']} with price {row['close']}")
                self.current_position = 'None'
                self.entry_price = None
                # Execute sell logic here (API call)

    def update_plot(self, frame, ax, line_market, line_tema, buy_scatter, sell_scatter):
        print("Frame updated once")

        # Get updated data
        df_tema = self.get_data()
        if df_tema is None:
            return ax, line_market, line_tema, buy_scatter, sell_scatter

        # Update the data for lines
        line_market.set_data(df_tema['timestamp'], df_tema['close'])
        line_tema.set_data(df_tema['timestamp'], df_tema['TEMA'])

        # Update the data for buy and sell points
        buy_signals = df_tema[df_tema['Signal'] == 1]
        sell_signals = df_tema[df_tema['Signal'] == -1]

        if not buy_signals.empty:
            buy_scatter.set_offsets(
                np.column_stack((buy_signals['timestamp'].astype(object), buy_signals['close'].astype(object))))
        else:
            buy_scatter.set_offsets(np.empty((0, 2)))

        if not sell_signals.empty:
            sell_scatter.set_offsets(
                np.column_stack((sell_signals['timestamp'].astype(object), sell_signals['close'].astype(object))))
        else:
            sell_scatter.set_offsets(np.empty((0, 2)))

        # Set the x and y limits dynamically to ensure full range visibility, including specific dates
        ax.set_xlim(df_tema['timestamp'].iloc[0], df_tema['timestamp'].iloc[-1])
        ax.set_ylim(df_tema['close'].min() - 5, df_tema['close'].max() + 5)

        # Set x-axis format to properly show dates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)

        # Execute the trade sequence for the updated data
        self.execute_trade_sequence()

        return ax, line_market, line_tema, buy_scatter, sell_scatter

    def plot(self):
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(14, 7))

        # Initialize the plots
        line_market, = ax.plot([], [], label='Market Value (Close)', color='blue', linewidth=2)
        line_tema, = ax.plot([], [], label='TEMA', color='orange', linewidth=2)
        buy_scatter = ax.scatter([], [], marker='^', s=100, color='green', label='Buy Signal')
        sell_scatter = ax.scatter([], [], marker='v', s=100, color='red', label='Sell Signal')

        # Set static plot elements (title, labels, legend)
        ax.set_title('Market Value, TEMA with Buy/Sell Signals')
        ax.set_ylabel('Value')
        ax.legend()

        # Create the animation, updating every 10 seconds (10000 milliseconds)
        ani = animation.FuncAnimation(
            fig, self.update_plot, fargs=(ax, line_market, line_tema, buy_scatter, sell_scatter),
            repeat_delay=0, frames=1, interval=10000, blit=False, cache_frame_data=False
        )

        # Show plot
        plt.show()

    def run(self):
        self.plot()

# Main
if __name__ == "__main__":
    bot = TradingBot(SYMBOL, TEMA_BAR, LIMIT)
    bot.run()
