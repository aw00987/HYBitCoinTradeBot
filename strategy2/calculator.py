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

def calculate_alligator_signal(df):
    df['jaw'] = talib.SMA(df['close'], 13)
    df['teeth'] = talib.SMA(df['close'], 8)
    df['lips'] = talib.SMA(df['close'], 5)
    # Define Alligator logic based on slope conditions for Jaw, Teeth, and Lips
    # Similar to the original approach but now includes separate slope checks
    # Add relevant calculations based on new rules