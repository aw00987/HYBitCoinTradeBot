import pandas as pd
import requests
import time
import hmac
import hashlib
import base64
import json

BASE_URL = "https://www.okx.com"
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
API_PASSPHRASE = 'your_api_passphrase'


def get_market_data(symbol, bar, limit):
    """
    获取市场数据
    :param symbol: 货币选择（默认美元每比特币）
    :param bar: K线周期
    :param limit: 周期数（limit个周期～至今）
    :return: DataFrame["事件戳timestamp","收盘价close"]
    """
    request_path = "/api/v5/market/candles"
    url = BASE_URL + request_path
    params = {
        "instId": symbol,
        "bar": bar,
        "limit": limit
    }
    response = requests.get(url, params)

    data = response.json()

    if data["code"] == "0":

        df = pd.DataFrame(data['data'], columns=[
            "timestamp", "open", "high", "low", "close", "volume", "quoteVolume", "volCcyQuote", "confirm"
        ])

        df = df.iloc[::-1].loc[:, ["timestamp", "close"]]

        # df['timestamp'] =  pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms')

        df[['close']] = df[['close']].astype(float)

        return df
    else:
        return None


def sign_request(timestamp, method, request_path, body):
    message = timestamp + method + request_path + body
    hmac_key = base64.b64decode(API_SECRET)
    signature = hmac.new(hmac_key, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def get_headers(method, request_path, body=''):
    timestamp = str(time.time())
    signature = sign_request(timestamp, method, request_path, body)
    headers = {
        'OK-ACCESS-KEY': API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': API_PASSPHRASE,
        'Content-Type': 'application/json'
    }
    return headers


def get_account_balance():
    """获取账户余额"""
    request_path = '/api/v5/account/balance'
    url = BASE_URL + request_path
    headers = get_headers('GET', request_path)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching balance: {response.text}")
        return None


def place_order(inst_id, side, size):
    """下单"""
    request_path = '/api/v5/trade/order'
    url = BASE_URL + request_path
    body = {
        "instId": inst_id,
        "side": side,
        "ordType": "market",
        "sz": size
    }
    headers = get_headers('POST', request_path, body=json.dumps(body))

    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error placing order: {response.text}")
        return None


def full_buy(inst_id, currency):
    """全仓买入指定交易对"""
    balance_info = get_account_balance()
    if balance_info:
        balance = float(next(b['availBal'] for b in balance_info['data'][0]['details'] if b['ccy'] == currency))
        print("账户余额：" + balance)
        if balance > 0:
            # 计算可以购买的数量
            order_response = place_order(inst_id, 'buy', balance)
            print("Buy order response:", order_response)
        else:
            print(f"No available {currency} balance to buy.")
    else:
        print("Failed to fetch balance.")


def full_sell(inst_id, currency):
    """全仓卖出指定交易对"""
    balance_info = get_account_balance()
    if balance_info:
        balance = float(next(b['availBal'] for b in balance_info['data'][0]['details'] if b['ccy'] == currency))
        if balance > 0:
            # 计算可以卖出的数量
            order_response = place_order(inst_id, 'sell', balance)
            print("Sell order response:", order_response)
        else:
            print(f"No available {currency} balance to sell.")
    else:
        print("Failed to fetch balance.")
