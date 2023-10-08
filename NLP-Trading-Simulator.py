import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import yfinance as yf
from datetime import datetime

class News:
    def __init__(self, url, highlights, sentiment, company_symbol, company_name):
        self.url = url
        self.highlights = highlights
        self.sentiment = sentiment
        self.company_symbol = company_symbol
        self.company_name = company_name

page = requests.get('https://api.marketaux.com/v1/news/all?exchanges=NYSE&filter_entities=true&limit=10&published_after=2023-02-19T21:21&api_token=668WuIXvMAeFigMNp6SftkC4nRrSG339SQbz4Qx7')
response = page.json()
nltk.download('vader_lexicon')

def analyze_sentiment(article):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(article)
    if sentiment_scores['compound'] > 0:
        return 'positive'
    elif sentiment_scores['compound'] < 0:
        return 'negative'
    else:
        return 'neutral'

allNews = []
for data in response['data']:
    url = data['url']
    highlights = set()
    sentiment = ''
    company_symbol = ''
    company_name = ''
    for entity in data['entities']:
        sentiment_score = entity['sentiment_score']
        if sentiment_score:
            if sentiment_score > 0.65:
                sentiment = 'positive'
            elif sentiment_score < 0.35:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        company_symbol = entity['symbol']
        company_name = entity['name']
        highlights.add(entity['highlights'][0]['highlight'])
    match = True
    for highlight in highlights:
        new_sentiment = analyze_sentiment(highlight)
        if sentiment != '':
            if new_sentiment != sentiment:
                match = False
        else:
            sentiment = new_sentiment
    if match:
        allNews.append(News(url, highlights, sentiment, company_symbol, company_name))

numberOfReliableArticles = len(allNews)
if numberOfReliableArticles == 1:
    print('Only 1 article was found.\n')
elif numberOfReliableArticles > 1:
    print(f'{numberOfReliableArticles} articles found.\n')
else:
    print('This algorithm did not find any reliable trades to make based on the articles provided by the API. Please try again later.\n')

for news in allNews:
    ticker = yf.Ticker(news.company_symbol)
    price_data = ticker.history(period='1d')
    price = round(price_data['Close'][0], 4)
    print('Article URL:')
    print(news.url)
    if news.sentiment == 'positive':
        print(f'The sentiment of this article is positive.')
        print(f'Bought {news.company_symbol} @ ${price}     {datetime.now().strftime("%H:%M:%S")}')
    elif news.sentiment == 'negative':
        print(f'The sentiment of this article is negative.')
        print(f'Sold {news.company_symbol} @ ${price}     {datetime.now().strftime("%H:%M:%S")}')
    else:
        print(f'The sentiment of this article is neutral - no trade will be executed.')
