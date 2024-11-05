import matplotlib.animation as animation
import matplotlib.pyplot as plt
import warnings


from calculator import *
from oks_api import *
import numpy as np

SYMBOL = "BTC-USDT"
TEMA_BAR = "1H"
ALLIGATOR_BAR = "1H"
LIMIT = 200
ZERO_THRESHOLD = 20
SECOND_DERIVATIVE_THRESHOLD = 4


def get_data():
    df_tema = get_market_data(SYMBOL, TEMA_BAR, LIMIT)
    calculate_tema_signal(df_tema, ZERO_THRESHOLD, SECOND_DERIVATIVE_THRESHOLD)

    df_alligator = get_market_data(SYMBOL, ALLIGATOR_BAR, LIMIT)
    calculate_alligator_signal(df_alligator)

    df_tema['timestamp'] = pd.to_datetime(df_tema['timestamp'], unit='ms')
    df_alligator['timestamp'] = pd.to_datetime(df_alligator['timestamp'], unit='ms')

    return df_tema, df_alligator


# Function to update the plot
def update_plot(frame, ax, line_market, line_tema, line_jaw, line_teeth, line_lips, buy_scatter,
                sell_scatter):

    print("frame updated once")

    # Call the data callback to get updated data
    df_tema, df_alligator = get_data()

    # Update the data for lines
    line_market.set_data(df_tema['timestamp'], df_tema['close'])
    line_tema.set_data(df_tema['timestamp'], df_tema['TEMA'])
    line_jaw.set_data(df_alligator['timestamp'], df_alligator['jaw'])
    line_teeth.set_data(df_alligator['timestamp'], df_alligator['teeth'])
    line_lips.set_data(df_alligator['timestamp'], df_alligator['lips'])

    # Update the data for buy and sell points
    buy_signals = df_tema[df_tema['Signal'] == 1]
    sell_signals = df_tema[df_tema['Signal'] == -1]

    if not buy_signals.empty:
        buy_scatter.set_offsets(np.column_stack((buy_signals['timestamp'].astype(object), buy_signals['close'].astype(object))))
    else:
        buy_scatter.set_offsets(np.empty((0, 2)))
    if not sell_signals.empty:
        sell_scatter.set_offsets(np.column_stack((sell_signals['timestamp'].astype(object), sell_signals['close'].astype(object))))
    else:
        sell_scatter.set_offsets(np.empty((0, 2)))

    # Set the x and y limits dynamically
    ax.set_xlim(df_tema['timestamp'].min(), df_tema['timestamp'].max())
    ax.set_ylim(min(df_tema['close'].min(), df_alligator['jaw'].min(), df_alligator['teeth'].min(),
                    df_alligator['lips'].min()) - 5,
                max(df_tema['close'].max(), df_alligator['jaw'].max(), df_alligator['teeth'].max(),
                    df_alligator['lips'].max()) + 5)

    return ax, line_market, line_tema, line_jaw, line_teeth, line_lips, buy_scatter, sell_scatter


def plot():
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(14, 7))

    # Initialize the plots
    line_market, = ax.plot([], [], label='Market Value (Close)', color='blue', linewidth=2)
    line_tema, = ax.plot([], [], label='TEMA', color='orange', linewidth=2)
    line_jaw, = ax.plot([], [], label='Alligator Jaw', color='red', linewidth=1.5)
    line_teeth, = ax.plot([], [], label='Alligator Teeth', color='green', linewidth=1.5)
    line_lips, = ax.plot([], [], label='Alligator Lips', color='yellow', linewidth=1.5)
    buy_scatter = ax.scatter([], [], marker='^', s=100, color='green', label='Buy Signal')
    sell_scatter = ax.scatter([], [], marker='v', s=100, color='red', label='Sell Signal')

    # Set static plot elements (title, labels, legend)
    ax.set_title('Market Value, TEMA, and Alligator with Buy/Sell Signals')
    ax.set_ylabel('Value')
    ax.legend()

    # Create the animation, updating every minute (60000 milliseconds)
    ani = animation.FuncAnimation(
        fig, update_plot, fargs=(ax, line_market, line_tema, line_jaw, line_teeth, line_lips, buy_scatter,
                                 sell_scatter),
        repeat_delay=0, frames=1, interval=10000, blit=False, cache_frame_data=False
    )

    # Show plot
    plt.show()


def main():
    plot()


if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    main()
