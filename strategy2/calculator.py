import talib

def calculate_tema_signal(df, zero_threshold, second_derivative_threshold):
    df["TEMA"] = talib.TEMA(df["close"], 20)
    df['f'] = df['TEMA'] - df['close']
    df['f_prime'] = df['f'].diff()
    df['f_double_prime'] = df['f_prime'].diff()

    # Initialize Signal column
    df['Signal'] = 0
    # Buy Signal: f close to 0, f' < 0, and f'' within a reasonable range
    df.loc[
        (abs(df['f']) <= zero_threshold) & (df['f_prime'] < 0) & (df['f_double_prime'] > -second_derivative_threshold),
        'Signal'
    ] = 1
    # Sell Signal: f close to 0, f' > 0, and f'' within a reasonable range
    df.loc[
        (abs(df['f']) <= zero_threshold) & (df['f_prime'] > 0) & (df['f_double_prime'] < second_derivative_threshold),
        'Signal'
    ] = -1

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

def calculate_alligator_signal(df):
    df['jaw'] = talib.SMA(df['close'], 13)
    df['teeth'] = talib.SMA(df['close'], 8)
    df['lips'] = talib.SMA(df['close'], 5)
    # Define Alligator logic based on slope conditions for Jaw, Teeth, and Lips
    # Similar to the original approach but now includes separate slope checks
    # Add relevant calculations based on new rules