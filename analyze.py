from calculator import *
from oks_api import *
from viewer import *

SYMBOL = "BTC-USDT"
BAR = "1m"
LIMIT = 100
ZERO_THRESHOLD = 10  # f接近0的阈值
SECOND_DERIVATIVE_THRESHOLD = 1  # f''合理范围的阈值


def main():
    # 拉取市场数据
    df = get_market_data(SYMBOL, BAR, LIMIT)
    # 计算买入卖出点
    calculate_signal(df, ZERO_THRESHOLD, SECOND_DERIVATIVE_THRESHOLD)
    # 终端输出计算结果
    terminal_output(df)
    # 图形输出k线
    plot(df)


if __name__ == "__main__":
    main()
