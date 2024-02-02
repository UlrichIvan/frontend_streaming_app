import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go

from utils.tools import COLUMNS_CHART, QUERY_FIELDS, SYMBOLS


# Initialize connection with mongodb
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


def get_data_from_ticker(ticker, stocks):
    stock_found = []
    for stock in stocks:
        if stock["_id"] == ticker:
            stock_found = stock["data"]
            break
    return stock_found


# get stocks in streaming mongo database after 1 min
@st.cache_data(ttl=60)
def get_stocks(_client):
    stock_db = _client.streaming_db
    stocks = stock_db.get_collection("stocks")
    data = list(
        stocks.aggregate(
            [
                {
                    "$project": QUERY_FIELDS,
                },
                {
                    "$match": {
                        "symbol": {"$in": SYMBOLS},
                    },
                },
                {
                    "$group": {"_id": "$symbol", "data": {"$push": "$$ROOT"}},
                },
            ],
        )
    )

    return data


# return the figure from chart associate to the specific symbol parameter and data frame
def get_figure(data_ticker, symbol):

    df = pd.DataFrame(
        data_ticker,
        columns=COLUMNS_CHART,
    )
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            name=symbol,
            x=pd.to_datetime(df["time"]),
            open=df["open"],
            high=df["high"],
            close=df["close"],
            low=df["low"],
        )
    )

    return fig
