import requests
import pandas as pd
import talib

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


def main():
    # 拉取市场数据
    df = get_market_data("BTC-USDT", "1m", 100)

    if df is not None:

        df["DEMA"] = talib.DEMA(df["close"], 20)

        print(df.tail())
    else:
        print("无法获取市场数据")


if __name__ == "__main__":
    main()
