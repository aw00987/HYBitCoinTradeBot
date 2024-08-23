import talib


def calculate_signal(df, zero_threshold, second_derivative_threshold):
    df["DEMA"] = talib.DEMA(df["close"], 20)
    df['f'] = df['DEMA'] - df['close']  # 定义dema和市值间的距离
    df['f_prime'] = df['f'].diff()  # 一阶差分
    df['f_double_prime'] = df['f_prime'].diff()  # 二阶差分
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
