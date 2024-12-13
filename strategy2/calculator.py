import talib

# def calculate_tema_signal(df, zero_threshold, second_derivative_threshold):
#     df["TEMA"] = talib.TEMA(df["close"], 20)
#     df['f'] = df['TEMA'] - df['close']
#     df['f_prime'] = df['f'].diff()
#     df['f_double_prime'] = df['f_prime'].diff()
#
#     # Initialize Signal column
#     df['Signal'] = 0
#     # Buy Signal: f close to 0, f' < 0, and f'' within a reasonable range
#     df.loc[
#         (abs(df['f']) <= zero_threshold) & (df['f_prime'] < 0) & (df['f_double_prime'] > -second_derivative_threshold),
#         'Signal'
#     ] = 1
#     # Sell Signal: f close to 0, f' > 0, and f'' within a reasonable range
#     df.loc[
#         (abs(df['f']) <= zero_threshold) & (df['f_prime'] > 0) & (df['f_double_prime'] < second_derivative_threshold),
#         'Signal'
#     ] = -1


def filter_frequent_signal(df):
    # 避免频繁交易 用相对价格变化率（百分比）过滤。例如只有当市值相对上次交易价格涨跌超过1%时才执行新交易。

    threshold_rate = 0.01  # 比如1%的价格变化率阈值
    last_trade_price = None

    for i, row in df.iterrows():
        sig = row['Signal']
        price = row['close']

        if sig != 0:  # 有买入(1)或卖出(-1)信号
            if last_trade_price is None:
                # 第一次产生信号，直接执行并记住这个价格
                last_trade_price = price
            else:
                # 计算相对价格变化率
                change_rate = abs(price - last_trade_price) / last_trade_price
                if change_rate < threshold_rate:
                    # 未达到阈值要求，将此信号过滤掉（变为0）
                    df.at[i, 'Signal'] = 0
                else:
                    # 达到阈值，更新last_trade_price
                    last_trade_price = price
        else:
            # signal == 0，无需修改
            pass


def filter_same_signal(df):
    # 去除相同的重复信号

    # 提前确保signal列为int类型（或至少是可比较类型）
    df['Signal'] = df['Signal'].astype(int)

    last_non_zero = 0  # 用于记录上一个非0信号
    adjusted_signals = []  # 存储调整后的信号

    for s in df['Signal']:
        if s == 0:
            # 当前信号为0则无需特别处理，直接加入结果
            adjusted_signals.append(s)
        else:
            # 当前信号为非0
            if s == last_non_zero:
                # 与上一个非0信号相同，需要忽略（变成0）
                adjusted_signals.append(0)
            else:
                # 不同非0信号，则更新last_non_zero并保留该信号
                adjusted_signals.append(s)
                last_non_zero = s

    # 将调整后的信号回写到DataFrame
    df['Signal'] = adjusted_signals


def simulate(df):

    # 初始条件
    wallet = 1.0  # 初始法币资金
    btc = 0.0     # 初始BTC数量
    started = False  # 是否已经遇到首个买入信号

    for idx, row in df.iterrows():
        close_price = row["close"]
        signal = row["Signal"]

        # 如果还没开始，只有遇到第一个买入信号才执行首次操作
        if not started:
            if signal == 1:
                # 全仓买入BTC
                btc = wallet / close_price
                wallet = 0.0
                started = True
            else:
                # 还没开始，非买入信号则不操作
                continue
        else:
            # 已经开始策略
            if signal == 1:
                # 有法币就买入BTC，如果目前资金都在BTC中则不操作
                if wallet > 0:
                    btc += wallet / close_price
                    wallet = 0.0
            elif signal == -1:
                # 有BTC就全部卖出换回法币，如果没有BTC则不操作
                if btc > 0:
                    wallet = btc * close_price
                    btc = 0.0
            # signal == 0: 不操作

    # 遍历完成后计算最终资产
    # 如果最后持有BTC，则将BTC全部按最后close价格转化为法币价值
    final_asset = wallet if btc == 0 else btc * df.iloc[-1]["close"]

    print("最终资产价值: ", final_asset)


def calculate_alligator_signal(df):
    df['jaw'] = talib.SMA(df['close'], 13)
    df['teeth'] = talib.SMA(df['close'], 8)
    df['lips'] = talib.SMA(df['close'], 5)
    # Define Alligator logic based on slope conditions for Jaw, Teeth, and Lips
    # Similar to the original approach but now includes separate slope checks
    # Add relevant calculations based on new rules