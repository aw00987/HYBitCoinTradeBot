from calculator import *
from oks_api import *

SYMBOL = "BTC-USDT"
BUY_CURRENCY = "USDT"
SELL_CURRENCY = "BTC"
BAR = "1m"
INTERVAL = 60
LIMIT = 100
ZERO_THRESHOLD = 10  # f接近0的阈值
SECOND_DERIVATIVE_THRESHOLD = 1  # f''合理范围的阈值


def main():
    last_operation = 0  # 记录上一次执行的操作，初始为0，表示未执行操作

    while True:
        start_time = time.time()
        # 拉取市场数据
        df = get_market_data(SYMBOL, BAR, LIMIT)
        # 计算买入卖出点
        calculate_signal(df, ZERO_THRESHOLD, SECOND_DERIVATIVE_THRESHOLD)
        # 拿到操作方式
        operation = df.tail(1)['Signal']
        # 根据策略调用api进行交易
        if operation == 1 and last_operation != 1:
            # 如果信号为买入，且上次操作不是买入
            full_buy('BTC-USDT', BUY_CURRENCY)
            last_operation = 1
        elif operation == -1 and last_operation != -1:
            # 如果信号为卖出，且上次操作不是卖出
            full_sell('BTC-USDT', SELL_CURRENCY)
            last_operation = -1
        last_operation = 0
        # 1分钟后再执行
        time.sleep(INTERVAL - time.time() + start_time)


if __name__ == "__main__":
    main()
