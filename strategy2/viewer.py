from matplotlib import pyplot as plt

def terminal_output(df):
    # Show output results
    print(df.columns.tolist())
    for index, row in df.iterrows():
        if row['Signal'] == 1:
            print(row.tolist())
        if row['Signal'] == -1:
            print(row.tolist())

def plot(df_tema, df_alligator):
    '''
    Output line chart with marked buy and sell points
    :param df_tema: ['timestamp', 'close', 'TEMA', 'Signal']
    :param df_alligator: ['timestamp', 'jaw', 'teeth', 'lips']
    :return:
    '''

    # Create a plot
    plt.figure(figsize=(14, 7))

    # Plot market value and TEMA line chart
    plt.plot(df_tema['timestamp'], df_tema['close'], label='Market Value (Close)', color='blue', linewidth=2)
    plt.plot(df_tema['timestamp'], df_tema['TEMA'], label='TEMA', color='orange', linewidth=2)

    # Plot Alligator lines (Jaw, Teeth, Lips)
    plt.plot(df_alligator['timestamp'], df_alligator['jaw'], label='Alligator Jaw', color='red', linewidth=1.5)
    plt.plot(df_alligator['timestamp'], df_alligator['teeth'], label='Alligator Teeth', color='green', linewidth=1.5)
    plt.plot(df_alligator['timestamp'], df_alligator['lips'], label='Alligator Lips', color='yellow', linewidth=1.5)

    # Mark buy and sell points
    buy_signals = df_tema[df_tema['Signal'] == 1]
    sell_signals = df_tema[df_tema['Signal'] == -1]

    plt.plot(buy_signals['timestamp'], buy_signals['close'], '^', markersize=10, color='green', label='Buy Signal')
    plt.plot(sell_signals['timestamp'], sell_signals['close'], 'v', markersize=10, color='red', label='Sell Signal')

    # Add title and labels
    plt.title('Market Value, TEMA, and Alligator with Buy/Sell Signals')
    # plt.xlabel('Timestamp')
    plt.ylabel('Value')
    # plt.xticks(rotation=45)
    plt.legend()

    # Show plot
    # plt.grid(True)
    plt.show()