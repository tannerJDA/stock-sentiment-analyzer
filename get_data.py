# gather stock news using finnhub api

from datetime import date, datetime
import finnhub
import requests
import time

import feedparser
from urllib.parse import quote_plus

finnhub_client = finnhub.Client(api_key="dblulh1r01qpfa5soeugdblulh1r01qpfa5soev0")

#print(finnhub_client.company_news('AAPL', _from="2026-06-01", to="2026-06-10"))


def gather_headlines(ticker, start_date):
    results = (finnhub_client.company_news(ticker, _from=start_date.strftime("%Y-%m-%d"), to=date.today().strftime("%Y-%m-%d")))

    return results


def gather_sector_news(ticker):

    # get company info
    comp_profile = finnhub_client.company_profile2(symbol=ticker)

    print(comp_profile)
    
    comp_sector = comp_profile['finnhubIndustry']
    print(f'{ticker} industry: {comp_sector}')

    # get general news in the date range
    gen_news = finnhub_client.general_news('general', min_id=0)

    return gen_news, comp_sector 



# -=-=-=- DOES NOT WORK -=-=-=-
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


# returns google news feed results based on query
#
# this function is used for sector wide news on the dashboard
# and combines multiple different querys for more results
def google_news_feed(query, time):

    #query = query + " industry news" + " when:30d"

    time_span = f"when:{time}"

    query_list = [
        f"{query} industry news {time_span}",
        f"{query} stocks {time_span}",
        f"{query} {time_span}"
    ]

    results = []

    for q in query_list:
        url = (
            "https://news.google.com/rss/search"
            f"?q={quote_plus(q)}"
            "&hl=en-US&gl=US&ceid=US:en"
        )

        feed = feedparser.parse(url)

        for article in feed.entries:
            results.append({
                "headline": article.title,
                "url": article.link,
                #"published": date.fromisoformat(article.get("published")),
                "published": datetime.strptime(article.get("published"), "%a, %d %b %Y %H:%M:%S %Z"),
                "source": article.get("source", {}).get("title", "")
            })
        

 
    results = parse_article_results(results) # remove duplicate results
    print(f'Oldest article returned: {get_oldest_article(results)}')
    return results


# take in a list of article results in remove duplicates
def parse_article_results(articles):

    results = []
    for art in articles:
        if art not in results:
            results.append(art)

    return results

# this is just for debugging the date entry button
def get_oldest_article(articles, tag='published'):
    #print(f'articles: \n{articles}')
    #print(f'date: {articles[0]['published']} || {date(articles[0]['published'])}')
    oldest = articles[0]

    for art in articles[1:]:
        if art[tag] < oldest[tag]:
            oldest = art

    return oldest