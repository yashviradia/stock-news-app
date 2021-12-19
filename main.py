import requests
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os
from twilio.rest import Client

load_dotenv(find_dotenv())

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

AV_Endpoint = os.environ.get("AV_Endpoint")
AV_api_key = os.environ.get("AV_api_key")

AV_parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": AV_api_key,
}

stock_price_response = requests.get(AV_Endpoint, params=AV_parameters)
stock_price_response.raise_for_status()
stock_price_data = stock_price_response.json()

gestern_stock_price = stock_price_data["Time Series (Daily)"]["2021-12-17"]["4. close"]
vorgestern_stock_price = stock_price_data["Time Series (Daily)"]["2021-12-16"]["4. close"]
difference_stock_price = int(float(gestern_stock_price) - float(vorgestern_stock_price))
percentage_change = round((difference_stock_price / float(gestern_stock_price)) * 100, 2)

if percentage_change > 5 or percentage_change < -5:
    NEWS_Endpoint = os.environ.get("NEWS_Endpoint")
    NEWS_api_key = os.environ.get("NEWS_api_key")

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    NEWS_parameters = {
        "q": COMPANY_NAME,
        "apiKey": NEWS_api_key,
    }

    news_response = requests.get(NEWS_Endpoint, params=NEWS_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()

    news_slice = news_data["articles"][:3]

    for news_article in news_slice:
        news_headline = news_article["title"]
        news_brief = news_article["content"]

        if percentage_change < -5:
            message = client.messages.create(
                body=f"TSLA: 🔻{abs(percentage_change)} \n Headline: {news_headline} \n Brief: {news_brief}",
                from_=os.environ.get("SENDER_NUMBER"),
                to=os.environ.get("RECEIVER_NUMBER")
            )
            print(message.status)

        else:
            message = client.messages.create(
                body=f"TSLA: 🔺{abs(percentage_change)} \n Headline: {news_headline} \n Brief: {news_brief}",
                from_=os.environ.get("SENDER_NUMBER"),
                to=os.environ.get("RECEIVER_NUMBER")
            )
            print(message.status)

