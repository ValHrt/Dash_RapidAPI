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

print(crypto_names)

# For testing only, to be modified later

app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Crypto Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children=[
        html.Br(),
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(options = crypto_names,
                     value = ['btc', 'eth'],
                     multi=True),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
