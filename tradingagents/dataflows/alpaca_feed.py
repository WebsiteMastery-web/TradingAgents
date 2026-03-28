import os, pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, CryptoLatestBarRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
load_dotenv("/root/limitless-ai/TradingAgents/.env")

def get_data_client():
    return CryptoHistoricalDataClient()

def get_ohlcv(symbol="BTC/USD", interval="1Day", lookback_days=90):
    client = get_data_client()
    tf = TimeFrame.Day if "Day" in interval else TimeFrame.Hour
    req = CryptoBarsRequest(symbol_or_symbols=symbol, timeframe=tf,
                            start=datetime.now()-timedelta(days=lookback_days))
    bars = client.get_crypto_bars(req)
    df = bars.df
    if isinstance(df.index, pd.MultiIndex):
        df = df.droplevel(0)
    logger.info(f"Fetched {len(df)} bars for {symbol}")
    return df

def get_current_price(symbol="BTC/USD"):
    client = get_data_client()
    req = CryptoLatestBarRequest(symbol_or_symbols=symbol)
    bar = client.get_crypto_latest_bar(req)
    price = float(bar[symbol].close)
    logger.info(f"Current {symbol} price: {price}")
    return price

def get_paper_balance():
    from alpaca.trading.client import TradingClient
    client = TradingClient(os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY"), paper=True)
    account = client.get_account()
    return {"buying_power": float(account.buying_power), "equity": float(account.equity)}
