import pandas as pd
import requests

BASE_URL = "https://www.okx.com/api/v5"
def get_market_data(symbol, bar, limit):
    '''
    获取市场数据
    :param symbol: 货币选择（默认美元每比特币）
    :param bar: K线周期
    :param limit: 周期数（limit个周期～至今）
    :return: DataFrame["事件戳timestamp","收盘价close"]
    '''
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
