import requests
import os

API_KEY = os.environ.get("RAPID_API_KEY")

url = "https://coingecko.p.rapidapi.com/simple/supported_vs_currencies"

headers = {
	"X-RapidAPI-Key": API_KEY,
	"X-RapidAPI-Host": "coingecko.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

print(response.text)
