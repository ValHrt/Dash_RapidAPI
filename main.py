from dash import Dash, html, dcc
import requests
import os

API_KEY = os.environ.get("RAPID_API_KEY")

url = "https://coingecko.p.rapidapi.com/simple/supported_vs_currencies"

headers = {
	"X-RapidAPI-Key": API_KEY,
	"X-RapidAPI-Host": "coingecko.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

crypto_str = response.text

crypto_names = eval(crypto_str)

app = Dash(__name__)


app.layout = html.Div(children=[
    html.H1(
        children='Crypto Dashboard',
    ),

    html.Div(children=[
        html.Br(),
        html.Label('Crypto-Currencies'),
        dcc.Dropdown(options = crypto_names,
                     value = ['btc', 'eth'],
                     multi=True),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
