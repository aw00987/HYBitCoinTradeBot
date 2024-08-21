import requests
import pandas as pd
import talib
import numpy as np
import matplotlib.pyplot as plt

# OKX API URL
BASE_URL = "https://www.okx.com/api/v5"


# 获取市场数据
def get_market_data(symbol="BTC-USDT", bar="1m", limit=100):
    url = f"{BASE_URL}/market/candles"

    params = {
        "instId": symbol,
        "bar": bar,
        "limit": limit
    }

    response = requests.get(url, params=params)

    data = response.json()

    if data["code"] == "0":

        df = pd.DataFrame(data['data'], columns=[
            "timestamp", "open", "high", "low", "close", "volume", "quoteVolume", "volCcyQuote", "confirm"
        ])

        df = df.iloc[::-1].loc[:, ["timestamp", "close"]]

        df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')

        df[['close']] = df[['close']].astype(float)

        return df
    else:
        return None


def plot(df):

    # 假设已经准备好了DataFrame df，其中包括 'timestamp', 'close', 'DEMA', 'Signal'

    # 创建图形
    plt.figure(figsize=(14, 7))

    # 画出市值和DEMA折线图
    plt.plot(df['timestamp'], df['close'], label='Market Value (Close)', color='blue', linewidth=2)
    plt.plot(df['timestamp'], df['DEMA'], label='DEMA', color='orange', linewidth=2)

    # 标记买点和卖点
    buy_signals = df[df['Signal'] == 1]
    sell_signals = df[df['Signal'] == -1]

    plt.plot(buy_signals['timestamp'], buy_signals['close'], '^', markersize=10, color='green', label='Buy Signal')
    plt.plot(sell_signals['timestamp'], sell_signals['close'], 'v', markersize=10, color='red', label='Sell Signal')

    # 添加标题和标签
    plt.title('Market Value and DEMA with Buy/Sell Signals')
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.xticks(rotation=45)  # 使时间戳标签倾斜以防重叠
    plt.legend()

    # 显示图形
    plt.grid(True)
    plt.show()



def main():
    # 拉取市场数据
    df = get_market_data("BTC-USDT", "1m", 200)

    if df is not None:

        df["DEMA"] = talib.DEMA(df["close"], 20)

        print("最近5分钟的数据：")
        print(df.tail(5))

    else:
        print("无法获取市场数据")
        return

    print("------------基础数据获取完毕---------")

        # 计算 f, f' 和 f''
    df['f'] = df['DEMA'] - df['close']
    df['f_prime'] = df['f'].diff()  # 一阶差分
    df['f_double_prime'] = df['f_prime'].diff()  # 二阶差分

    # 定义阈值
    zero_threshold = 10  # f接近0的阈值
    second_derivative_threshold = 1  # f''合理范围的阈值

    # 初始化信号列
    df['Signal'] = 0

    # 买入信号：f接近0, f' < 0, 且 f'' 在合理范围内
    df.loc[
        (abs(df['f']) <= zero_threshold) &
        (df['f_prime'] < 0) &
        (df['f_double_prime'] > -second_derivative_threshold),
        'Signal'
    ] = 1  # 1表示买入信号

    # 卖出信号：f接近0, f' > 0, 且 f'' 在合理范围内
    df.loc[
        (abs(df['f']) <= zero_threshold) &
        (df['f_prime'] > 0) &
        (df['f_double_prime'] < second_derivative_threshold),
        'Signal'
    ] = -1  # -1表示卖出信号

    # 显示结果
    # 打印表头
    print(df.columns.tolist())

    # 逐行打印数据
    for index, row in df.iterrows():
        if row['Signal'] == 1:
            print(row.tolist())
        if row['Signal'] == -1:
            print(row.tolist())

    plot(df)

if __name__ == "__main__":
    main()

