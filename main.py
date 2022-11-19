import requests
from newsapi import NewsApiClient
from twilio.rest import Client
from datetime import datetime, timedelta
import os
######################################## DATE ########################################
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_formatted = datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=16, minute=30)
day_before_yesterday = today - timedelta(days=2)
day_before_yesterday_formatted = datetime(year=day_before_yesterday.year, month=day_before_yesterday.month,
                                          day=day_before_yesterday.day, hour=16, minute=30)
######################################## STOCK DATA #################################
STOCK_API_KEY = os.environ.get('STOCK_API_KEY')
response = requests.get(
    f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AMZN&interval=30min&apikey='
    f'{STOCK_API_KEY}')
data = response.json()
yesterday_close = data['Time Series (30min)'][str(yesterday_formatted)]['4. close']  # gets yesterday's closing price
day_before_yesterday_close = data['Time Series (30min)'][str(day_before_yesterday_formatted)]['4. close']  # gets day
# before yesterday's closing price
######################################## NEWS DATA ########################################
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
all_articles = newsapi.get_everything(
    sources='bbc-news,the-verge',
    domains='bbc.co.uk,techcrunch.com',
    from_param=day_before_yesterday_formatted,
    to=yesterday_formatted,
    language='en',
    sort_by='relevancy',
    page=1)
######################################## TWILIO DATA #################################
account_sid = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')

difference = float(yesterday_close) - float(day_before_yesterday_close)
percent_difference = float(difference) / float(day_before_yesterday_close) * 100  # checks percentage difference of
# stock
if percent_difference > 1 or percent_difference < 1:
    global titles_split
    for index in range(0, len(all_articles['articles'])):  # iterates through news article titles
        titles = all_articles['articles'][index]['title']  # accesses article titles
        titles_split = titles.split()  # splits article titles into lists
        if 'Amazon' in titles_split:  # iterates through article titles checking for keyword 'Amazon'
            client = Client(account_sid, auth_token)   # sends text message
            URL = all_articles['articles'][index]['url']  # accesses link to article
            if percent_difference > 1:
                message = client.messages.create(
                    body=f'Amazon stock is 🔺 {round(percent_difference, 2)}% from {day_before_yesterday.date()}.'
                         f'\n {URL}',
                    from_= os.environ.get('from'),
                    to=os.environ.get('to')
                )
                break
            elif percent_difference < -1:
                message = client.messages.create(
                    body=f'Amazon stock is 🔻 {round(percent_difference, 2) * -1}% from {day_before_yesterday.date()}.'
                         f'\n {URL}',
                    from_=os.environ.get('from'),
                    to=os.environ.get('to')
                )
                break
