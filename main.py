from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import requests
import os

API_KEY = os.environ.get("RAPID_API_KEY")

url_vs_currency = "https://coingecko.p.rapidapi.com/simple/supported_vs_currencies"
url_coins = "https://coingecko.p.rapidapi.com/coins/list"
url_price = "https://coingecko.p.rapidapi.com/simple/price"

headers = {
	"X-RapidAPI-Key": API_KEY,
	"X-RapidAPI-Host": "coingecko.p.rapidapi.com"
}

querystring_price = {"ids":"bitcoin","vs_currencies":"eur"}

response_vs_currency = requests.request("GET", url_vs_currency, headers=headers)
response_coins = requests.request("GET", url_coins, headers=headers)
response_price = requests.request("GET", url_price, headers=headers,
                                  params=querystring_price)

vs_currency = eval(response_vs_currency.text)
coins_glob = eval(response_coins.text)
price = eval(response_price.text)

coins_id = [coin['id'] for coin in coins_glob]
coins_name = [coin['name'] for coin in coins_glob]
coin_price = price['bitcoin']['eur']


app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        children='Crypto Dashboard',
    ),

    html.Div(children=[
        html.Br(),
        html.Label('Target Currency'),
        dcc.Dropdown(id = "Currency_Selected",
                     options = vs_currency,
                     value = 'eur'),
    ]),

    html.Div(children=[
        html.Br(),
        html.Label('Cryptocurrency'),
        dcc.Dropdown(id = "Coin_Selected",
                     options = coins_name,
                     value = 'Bitcoin'),
    ]),

    html.H3(id="current_price", style={'text-align': 'center',
                                       'color': '#FD841F'})
])


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
