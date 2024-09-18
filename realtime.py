import matplotlib.dates as mdates
import numpy as np
from matplotlib.animation import FuncAnimation

from calculator import *
from oks_api import *
from viewer import *

SYMBOL = "BTC-USDT"
BAR = "1m"
LIMIT = 100
ZERO_THRESHOLD = 10  # f接近0的阈值
SECOND_DERIVATIVE_THRESHOLD = 1  # f''合理范围的阈值

ani = None  # 声明全局变量

def get_data():
    df = get_market_data(SYMBOL, BAR, LIMIT)
    calculate_signal(df, ZERO_THRESHOLD, SECOND_DERIVATIVE_THRESHOLD)
    df['timestamp'] = mdates.date2num(df['timestamp'])
    return df


# 动态更新函数
def update_plot(frame, df, line1, line2, scatter_buy, scatter_sell):
    print("start update")

    # 获取最新数据
    new_data = get_data()

    # 更新折线数据
    line1.set_data(new_data['timestamp'], new_data['close'])
    line2.set_data(new_data['timestamp'], new_data['DEMA'])

    # 更新买点和卖点
    buy_signals = new_data[new_data['Signal'] == 1]
    sell_signals = new_data[new_data['Signal'] == -1]

    # 更新散点数据
    scatter_buy.set_offsets(np.c_[buy_signals['timestamp'], buy_signals['close']])
    scatter_sell.set_offsets(np.c_[sell_signals['timestamp'], sell_signals['close']])

    # 动态调整x轴范围和y轴范围
    plt.xlim(new_data['timestamp'].iloc[0], new_data['timestamp'].iloc[-1])
    plt.ylim(min(new_data['close'].min(), new_data['DEMA'].min()) - 100,
             max(new_data['close'].max(), new_data['DEMA'].max()) + 100)

    return line1, line2, scatter_buy, scatter_sell


def animate(df):
    '''
    输出实时更新的折现图，标记买点和卖点
    :param df: ['timestamp', 'close', 'DEMA', 'Signal']
    :return:
    '''

    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 7))

    # 初始图形数据
    line1, = ax.plot(df['timestamp'], df['close'], label='Market Value (Close)', color='blue', linewidth=2)
    line2, = ax.plot(df['timestamp'], df['DEMA'], label='DEMA', color='orange', linewidth=2)

    # 初始化买点和卖点的散点图
    buy_signals = df[df['Signal'] == 1]
    sell_signals = df[df['Signal'] == -1]

    scatter_buy = ax.scatter(buy_signals['timestamp'], buy_signals['close'], marker='^', color='green',
                             label='Buy Signal', s=100)
    scatter_sell = ax.scatter(sell_signals['timestamp'], sell_signals['close'], marker='v', color='red',
                              label='Sell Signal', s=100)

    # 设置标题和标签
    ax.set_title('Market Value and DEMA with Buy/Sell Signals')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Value')
    ax.legend()
    plt.xticks(rotation=45)  # 使时间戳标签倾斜以防重叠
    ax.grid(True)

    # 创建动画，设置interval为60000毫秒(1分钟)
    ani = FuncAnimation(
        fig, update_plot, fargs=(df, line1, line2, scatter_buy, scatter_sell), interval=60000,cache_frame_data=False
    )

    # 显示图形
    plt.show()


if __name__ == "__main__":
    # 初始化数据
    initial_data = get_data()
    animate(initial_data)
