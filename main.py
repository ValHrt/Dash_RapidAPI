from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import requests
import datetime as dt
import os

API_KEY = os.environ.get("RAPID_API_KEY")

######################### URL ######################### 
url_vs_currency = "https://coingecko.p.rapidapi.com/simple/supported_vs_currencies"
url_coins = "https://coingecko.p.rapidapi.com/coins/list"
url_price = "https://coingecko.p.rapidapi.com/simple/price"
# Coin selected is directly included in url instead of headers for this
# endpoint!
url_market = "https://coingecko.p.rapidapi.com/coins/bitcoin/market_chart"

######################### HEADERS ######################### 
headers = {
	"X-RapidAPI-Key": API_KEY,
	"X-RapidAPI-Host": "coingecko.p.rapidapi.com"
}

######################### QUERYSTRINGS ######################### 
querystring_price = {"ids":"bitcoin","vs_currencies":"eur"}
querystring_market = {"vs_currency":"eur","days":"2"}

######################### RESPONSES ######################### 
response_vs_currency = requests.request("GET", url_vs_currency, headers=headers)
response_coins = requests.request("GET", url_coins, headers=headers)
response_price = requests.request("GET", url_price, headers=headers,
                                  params=querystring_price)
response_market = requests.request("GET", url_market, headers=headers,
                                   params=querystring_market)

######################### LOADING DATA FROM URL ######################### 
vs_currency = eval(response_vs_currency.text)
coins_glob = eval(response_coins.text)
price = eval(response_price.text)
market = response_market.json()

######################### DATA HANDLING ######################### 
coins_id = [coin['id'] for coin in coins_glob]
coins_name = [coin['name'] for coin in coins_glob]
coin_price = price['bitcoin']['eur']
# 1 data point == 1 hour
coin_market = [price[1] for price in market['prices']]

######################### DATETIME MODULE ######################### 
today = dt.datetime.now()

date_lst = [(dt.datetime.now() - dt.timedelta(hours = hour)).strftime("%d/%m/%Y %H:%M")
            for hour in range(len(coin_market))]
date_lst.reverse()

######################### PANDAS | PLOTLY ######################### 
df_market = pd.DataFrame({"Date": date_lst, "Price": coin_market})

price_fig = px.line(df_market, x = "Date", y = "Price", title = "Bitcoin price "
                    "in € on last 2 days")


######################### DASH APP ######################### 
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children='Crypto Dashboard',
    ),

    html.Div(id = 'options_div', children=[
        html.Div(children=[
            html.Br(),
            html.Label('Target Currency'),
            dcc.Dropdown(id = "Currency_Selected",
                         options = vs_currency,
                         value = 'eur'),
            html.Br(),
            html.Label('Cryptocurrency'),
            dcc.Dropdown(id = "Coin_Selected",
                         options = coins_name,
                         value = 'Bitcoin')],
                 style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Br(),
            html.Label('Select Range'),
            dcc.RadioItems(['Select from slider', 'Max range'], 'Select from slider'),

            html.Br(),
            html.Label('Number of days'),
            dcc.Slider(min = 2,
                       max = 365,
                       marks = {i: f'Day {i}' if i == 2 else str(i) for i in
                                range(1, 366) if i % 30 == 0 or i == 2},
                       value = 1)
        ],
                 style = {'padding': 10, 'flex': 1})],
        style={'display': 'flex', 'flex-direction': 'row'}),

    html.H3(id="current_price", style={'text-align': 'center',
                                       'color': '#FD841F'}),
    dcc.Graph(id="market_price", figure=price_fig)
])


######################### CALLBACKS ######################### 
@app.callback(
    Output(component_id = "current_price", component_property = "children"),
    [Input(component_id = "Currency_Selected", component_property = "value"),
     Input(component_id = "Coin_Selected", component_property = "value")])


def get_current_price(currency, coin):
    title = f"Current Bitcoin price: {coin_price}€"
    if currency and coin:
        index = coins_name.index(coin)
        querystring_price = {"ids": str(coins_glob[index]["id"]),
                             "vs_currencies":currency}
        response_price = requests.request("GET", url_price, headers=headers,
                                  params=querystring_price)
        price_new = eval(response_price.text)
        coin_price_new = price_new[str(coins_glob[index]["id"])][currency]

        if currency == "eur":
            title = f"Current {coin} price: {coin_price_new}€"
        elif currency == "usd":
            title = f"Current {coin} price: {coin_price_new}$"
        else:
            title = f"Current {coin} price: {coin_price_new} {currency.upper()}"
    return title

if __name__ == '__main__':
    app.run_server(debug=True)
