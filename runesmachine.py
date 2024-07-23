import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import websocket
import _thread
import json
import plotly.express as px
import folium
from streamlit_folium import st_folium
from openai import openai

# Set page configuration
st.set_page_config(page_title="BTC Market Analysis Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .navy-blue {
            background-color: #000080;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .container {
            background-color: #E64A19;
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        .neuromorphic {
            background-color: white;
            border: none;
            box-shadow: 10px 10px 20px #b0b0b0, -10px -10px 20px #ffffff;
            color: black;
            padding: 10px;
            margin: 10px 0;
            border-radius: 10px;
        }
        .neuromorphic:focus {
            outline: none;
        }
        .btn-black {
            background-color: black;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            cursor: pointer;
        }
        .btn-black:hover {
            background-color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Streamlit app
st.title("BTC Market Analysis Dashboard")

# Real-time Price Tracker
st.markdown('<div class="navy-blue"><h3>Real-time BTC Price Tracker</h3></div>', unsafe_allow_html=True)
btc_price = yf.Ticker("BTC-USD").info['regularMarketPrice']
st.metric("BTC Price (USD)", btc_price)

# Historical Data Visualization
st.markdown('<div class="navy-blue"><h3>Historical Data</h3></div>', unsafe_allow_html=True)
data = yf.download("BTC-USD", start="2020-01-01", end=pd.Timestamp.now().strftime("%Y-%m-%d"))
fig = px.line(data, x=data.index, y="Close", title='BTC Price Over Time')
st.plotly_chart(fig)

# Technical Analysis Tools
st.markdown('<div class="navy-blue"><h3>Technical Analysis</h3></div>', unsafe_allow_html=True)
st.write("Moving Averages")
ma_period = st.slider("Select Period", 1, 50, 20)
data[f"MA_{ma_period}"] = data['Close'].rolling(ma_period).mean()
fig_ma = px.line(data, x=data.index, y=["Close", f"MA_{ma_period}"], title=f'BTC Price with {ma_period}-Day Moving Average')
st.plotly_chart(fig_ma)

# News Feed
st.markdown('<div class="navy-blue"><h3>News Feed</h3></div>', unsafe_allow_html=True)
news = pd.read_json("https://cryptopanic.com/api/v1/posts/?auth_token=API_KEY&currencies=BTC")
st.write(news[["title", "published_at"]])

# Portfolio Tracker
st.markdown('<div class="navy-blue"><h3>Portfolio Tracker</h3></div>', unsafe_allow_html=True)
btc_holdings = st.number_input("Enter your BTC holdings", key="btc_holdings", format="%.6f")
portfolio_value = btc_holdings * btc_price
st.write(f"Your BTC portfolio value is ${portfolio_value:.2f}")

# Runes Overview
st.markdown('<div class="navy-blue"><h3>Runes Overview</h3></div>', unsafe_allow_html=True)
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
st.markdown('<div class="navy-blue"><h3>Ordinals Data</h3></div>', unsafe_allow_html=True)
ordinals_url = "https://api.ordinals.com/v1/ordinals"
ordinals_response = requests.get(ordinals_url)
ordinals_data = ordinals_response.json()
ordinals_df = pd.DataFrame(ordinals_data)
st.table(ordinals_df)

# Enhanced Portfolio Tracker
st.markdown('<div class="navy-blue"><h3>Enhanced Portfolio Tracker</h3></div>', unsafe_allow_html=True)
rune_holdings = st.number_input("Enter your rune holdings", key="rune_holdings", format="%.6f")
ordinal_holdings = st.number_input("Enter your ordinal holdings", key="ordinal_holdings", format="%.6f")
rune_value = 0  # Calculate based on rune data
ordinal_value = 0  # Calculate based on ordinal data
total_value = portfolio_value + rune_value + ordinal_value
st.write(f"Your total portfolio value is ${total_value:.2f}")

# Mempool Data
st.markdown('<div class="navy-blue"><h3>Mempool Data</h3></div>', unsafe_allow_html=True)
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
    ws.run_forever()

_thread.start_new_thread(run_websocket, ())

# Data Plotting
st.markdown('<div class="navy-blue"><h3>Data Plotting</h3></div>', unsafe_allow_html=True)
st.write("You can plot your data here.")

# Mapping
st.markdown('<div class="navy-blue"><h3>Mapping</h3></div>', unsafe_allow_html=True)
m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
folium.Marker([45.5236, -122.6750], popup="BTC Event").add_to(m)
st_folium(m, width=700, height=500)

# Chatbot
st.markdown('<div class="navy-blue"><h3>Chatbot</h3></div>', unsafe_allow_html=True)
st.write("Ask questions about the data.")

openai.api_key = "your_openai_api_key"

def query_openai(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=100
    )
    return response.choices[0].text.strip()

user_query = st.text_input("Ask a question about BTC data")
if user_query:
    answer = query_openai(user_query)
    st.write(answer)

# Keep the Streamlit app running
st.stop()
