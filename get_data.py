# gather stock news using finnhub api

from datetime import date
import finnhub
import requests
import time

import feedparser
from urllib.parse import quote_plus

finnhub_client = finnhub.Client(api_key="dblulh1r01qpfa5soeugdblulh1r01qpfa5soev0")

#print(finnhub_client.company_news('AAPL', _from="2026-06-01", to="2026-06-10"))


def gather_headlines(ticker, start_date):
    return (finnhub_client.company_news(ticker, _from=start_date.strftime("%Y-%m-%d"), to=date.today().strftime("%Y-%m-%d")))


def gather_sector_news(ticker):

    # get company info
    comp_profile = finnhub_client.company_profile2(symbol=ticker)

    print(comp_profile)
    
    comp_sector = comp_profile['finnhubIndustry']
    print(f'{ticker} industry: {comp_sector}')

    # get general news in the date range
    gen_news = finnhub_client.general_news('general', min_id=0)

    return gen_news, comp_sector




def get_gdelt_news(ticker):
    gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": 'aapl',
        "mode": 'artlist',
        "maxrecords": 100,
        "timespan": "30d",
        "format": "json"
    }

    try:
        response = requests.get(gdelt_url, params=params, timeout=30)
        response.raise_for_status()

    except requests.RequestException as e:
        print(f'Experiencing an error: {e}')

        # too many requests
        while response.status_code == 429:
            # wait
            time.sleep(5)

            # retry
            response = requests.get(gdelt_url, params=params, timeout=30)
            response.raise_for_status()

    

    articles = response.json().get("articles", [])
    for a in articles:
        print(f"{a}\n------\n")



def google_news_feed(query):

    query = query + " when:30d"
    # translate raw query into url safe string
    encoded_query = quote_plus(query)

    url = (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(url)

    results = []

    for article in feed.entries:
        results.append({
            "headline": article.title,
            "url": article.link,
            "published": article.get("published"),
            "source": article.get("source", {}).get("title", "")
        })

    return results

'''news = google_news_feed("aapl")
for n in news:
    print(f"{n}\n------\n")
'''
'''
#print (gather('AAPL', date(year=2026, month=11, day=1)))

news, sec = gather_sector_news('aapl')

for n in news:

    if n['category'].lower() == sec.lower():
        print(n)
        print('------\n')
'''

