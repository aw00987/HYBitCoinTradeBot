from matplotlib import pyplot as plt


def terminal_output(df):
    # 显示结果
    print(df.columns.tolist())
    for index, row in df.iterrows():
        if row['Signal'] == 1:
            print(row.tolist())
        if row['Signal'] == -1:
            print(row.tolist())


def plot(df):
    '''
    输出折现图，标记买点和卖点
    :param df: ['timestamp', 'close', 'DEMA', 'Signal']
    :return:
    '''

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
