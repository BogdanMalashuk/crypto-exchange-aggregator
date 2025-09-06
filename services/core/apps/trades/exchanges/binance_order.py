from binance.client import Client

API_KEY = 'fNBN2ZOAf9JqCzN6Qus7zL5XPPP6Ri9D5XYpeCfnXMWkmbpMZ2KJRzep0JxC6Xk9'
API_SECRET = 'ZSifAu3Pc2mvr0RYh2edu3xgI7jiojT6vhqofLYtd4rItu8EnPveRZecTFVLmsuZ'

client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = 'https://testnet.binance.vision/api'


def create_sell_order(symbol: str, quantity: float):
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )
    return order
