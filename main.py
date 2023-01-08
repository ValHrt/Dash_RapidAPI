from dash import Dash, html, dcc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import requests
import datetime as dt
import os

# TODO: include exchange volume on hover

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
querystring_market = {"vs_currency":"eur","days":"max"}

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

date_lst = [(dt.datetime.now() - dt.timedelta(hours = day * 24)).date()
            for day in range(len(coin_market))]
date_lst.reverse()

######################### PANDAS | PLOTLY ######################### 
df_market = pd.DataFrame({"Date": date_lst, "Price": coin_market})
print(df_market.dtypes)

price_fig = px.line(df_market, x = "Date", y = "Price", title = "Bitcoin price "
                    "evolution in €")

date_buttons = [
    {'count': 12, 'step': "month", 'stepmode': "todate", 'label': "1YTD"},
    {'count': 6, 'step': "month", 'stepmode': "todate", 'label': "6MTD"},
    {'count': 3, 'step': "month", 'stepmode': "todate", 'label': "3MTD"},
    {'count': 1, 'step': "month", 'stepmode': "todate", 'label': "1MTD"},
    {'count': 14, 'step': "day", 'stepmode': "todate", 'label': "2WTD"}]


def annotate_plot(df, choice):
    if choice == "min":
        idx = df[["Price"]].idxmin()
        color = "red"

    elif choice == "max":
        idx = df[["Price"]].idxmax()
        color = "green"

    else:
        raise ValueError("Only min and max can be passed to the function as "
        "choice argument!")

    annot = {
        'x': df.loc[idx]["Date"].values[0],
        'y': df.loc[idx]["Price"].values[0],
        'showarrow': True, 'arrowhead': 3,
        'text': f'{choice.title()} price: {round(df.loc[idx]["Price"].array[0], 2)}',
        'font': {'size': 10, 'color': color}}

    print(annot)

    return annot


price_fig.update_layout(
    {'xaxis': {'rangeselector': {
        'buttons': date_buttons}},
     'annotations': [annotate_plot(df_market, "min"), annotate_plot(df_market, "max")]})

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


        html.Div(id = 'text_div', children=[
            html.H2(id="current_price"),
            html.H2(id='request_time')],
            style={'text-align': 'center', 'color': '#FD841F', 'padding': 10,
                   'flex': 1})],
        style={'display': 'flex', 'flex-direction': 'row'}),
    dcc.Graph(id="market_price", figure=price_fig)
])


######################### CALLBACKS ######################### 
@app.callback(
    [Output(component_id = "current_price", component_property = "children"),
     Output(component_id = "request_time", component_property = "children")],
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
        title = f"Current {coin} price: {coin_price_new} {usd_eur_symbol(currency)}"

    return title, f'Request time: {dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'


@app.callback(
    Output(component_id = "market_price", component_property = "figure"),
    [Input(component_id = "Currency_Selected", component_property = "value"),
     Input(component_id = "Coin_Selected", component_property = "value"),
     Input(component_id = "market_price", component_property = "relayoutData")])


def update_figure(currency, coin, relayout_data):
    if currency and coin:
        index = coins_name.index(coin)
        crypto_id = str(coins_glob[index]["id"])
        url_market_new = f"https://coingecko.p.rapidapi.com/coins/{crypto_id}/market_chart"
        querystring_market_new = {"vs_currency": currency, "days":"max"}
        response_market_new = requests.request("GET", url_market_new, headers=headers,
                                        params=querystring_market_new)
        market_new = response_market_new.json()
        coin_market_new = [price[1] for price in market_new['prices']]
        date_lst_new = [(dt.datetime.now() - dt.timedelta(hours = day * 24))
                    for day in range(len(coin_market_new))]
        date_lst_new.reverse()
        df_market_new = pd.DataFrame({"Date": date_lst_new, "Price":
                                      coin_market_new})
        price_fig = px.line(df_market_new, x = "Date", y = "Price", title =
                            f"{coin} price evolution in {usd_eur_symbol(currency)}")

        if (relayout_data is None) or ("xaxis.range[0]" not in relayout_data):
            raise PreventUpdate  # from dash.exceptions import PreventUpdate

        mask = (df_market_new['Date'] > relayout_data["xaxis.range[0]"]) &\
        (df_market_new['Date'] <= relayout_data["xaxis.range[1]"])

        df_market_new["Date"] = df_market_new["Date"].dt.date

        price_fig.update_yaxes(autorange = False)
        price_fig.update_layout(
            {'xaxis': {'rangeselector': {
                'buttons': date_buttons},
                       'range': [
                       df_market_new.loc[mask].iloc[0]["Date"],
                       df_market_new.loc[mask].iloc[-1]["Date"]]},
             'yaxis': {'range': [
             df_market_new.loc[mask]["Price"].min()*0.98,
             df_market_new.loc[mask]["Price"].max()*1.02]},
             'annotations': [annotate_plot(df_market_new.loc[mask], 'min'),
                             annotate_plot(df_market_new.loc[mask], 'max')]})
        print(annotate_plot(df_market_new.loc[mask], 'max'))
    return price_fig


def usd_eur_symbol(currency: str):
    if currency == "eur":
        return "€"
    elif currency == "usd":
        return "$"
    return currency.upper()


def convert_timestamp(time):
    return dt.datetime.utcfromtimestamp(time.tolist()/1e9).date()

if __name__ == '__main__':
    app.run_server(debug=True)
