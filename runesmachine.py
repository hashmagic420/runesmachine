import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import websocket
import _thread
import json
import time

# Initialize Streamlit app
st.title("BTC Market Analysis Dashboard")

# Real-time Price Tracker
btc_price = yf.Ticker("BTC-USD").info['regularMarketPrice']
st.metric("BTC Price (USD)", btc_price)

# Historical Data Visualization
st.header("Historical Data")
data = yf.download("BTC-USD", start="2020-01-01", end=pd.Timestamp.now().strftime("%Y-%m-%d"))
st.line_chart(data['Close'])

# Technical Analysis Tools
st.header("Technical Analysis")
st.write("Moving Averages")
ma_period = st.slider("Select Period", 1, 50, 20)
data[f"MA_{ma_period}"] = data['Close'].rolling(ma_period).mean()
st.line_chart(data[[f"MA_{ma_period}", "Close"]])

# News Feed
st.header("News Feed")
news = pd.read_json("https://cryptopanic.com/api/v1/posts/?auth_token=API_KEY&currencies=BTC")
st.write(news[["title", "published_at"]])

# Portfolio Tracker
st.header("Portfolio Tracker")
btc_holdings = st.number_input("Enter your BTC holdings")
portfolio_value = btc_holdings * btc_price
st.write(f"Your BTC portfolio value is ${portfolio_value:.2f}")

# Runes Overview
st.header("Runes Overview")
runes_url = "https://luminex.io/runes/alpha"
response = requests.get(runes_url)
soup = BeautifulSoup(response.content, 'html.parser')
runes_data = []  # Extract relevant runes data from the HTML
for rune in soup.find_all('div', class_='rune-class'):  # Example class
    name = rune.find('h2').text
    value = rune.find('span', class_='value-class').text  # Example class
    runes_data.append({"Name": name, "Value": value})

runes_df = pd.DataFrame(runes_data)
st.table(runes_df)

# Ordinals Data
st.header("Ordinals Data")
ordinals_url = "https://api.ordinals.com/v1/ordinals"
ordinals_response = requests.get(ordinals_url)
ordinals_data = ordinals_response.json()
ordinals_df = pd.DataFrame(ordinals_data)
st.table(ordinals_df)

# Enhanced Portfolio Tracker
st.header("Enhanced Portfolio Tracker")
rune_holdings = st.number_input("Enter your rune holdings")
ordinal_holdings = st.number_input("Enter your ordinal holdings")
rune_value = 0  # Calculate based on rune data
ordinal_value = 0  # Calculate based on ordinal data
total_value = portfolio_value + rune_value + ordinal_value
st.write(f"Your total portfolio value is ${total_value:.2f}")

# Mempool Data
st.header("Mempool Data")

mempool_data = st.empty()

def on_message(ws, message):
    data = json.loads(message)
    mempool_data.write(data)

def on_error(ws, error):
    st.write(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    st.write("### Mempool connection closed ###")

def on_open(ws):
    message = { "action": "init" }
    ws.send(json.dumps(message))
    message = { "action": "want", "data": ['blocks', 'stats', 'mempool-blocks', 'live-2h-chart', 'watch-mempool'] }
    ws.send(json.dumps(message))

def run_websocket():
    ws = websocket.WebSocketApp("wss://mempool.space/api/v1/ws",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection

_thread.start_new_thread(run_websocket, ())

# Keep the Streamlit app running
st.stop()
