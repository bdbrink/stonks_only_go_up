import yfinance as yf
from iexcloud import IEXCloud
import numpy as np
import datetime
import finnhub
import math
import logging
from datetime import datetime
from dateutil.parser import parse
from newsapi import NewsApiClient
from textblob import TextBlob
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

# Define ticker and date range for historical data
ticker = "AMZN"
start_date = datetime.datetime(2023, 10, 1)
end_date = datetime.datetime(2028, 12, 11)
# Initialize Finnhub client
finnhub_client = finnhub.Client()
client = IEXCloud(api_token)
quote = client.quote(ticker)


def year_to_date():

    # Get historical data from Yahoo
    hist_data = yf.download(ticker, start=start_date, end=end_date)

    # Combine historical data with real-time quote
    combined_data = hist_data.append(quote.to_frame().transpose())

    # Calculate YTD performance
    ytd_return = (combined_data["Close"][-1] - combined_data["Close"][0]) / combined_data["Close"][0] * 100

    return ytd_return


def analayst_recs():

    combined_data = year_to_date()

    analyst_recommendations = finnhub_client.recommendation(symbol=ticker, verbose=False)
    analyst_ratings = finnhub_client.analyst_ratings(symbol=ticker, verbose=False)

    # Extract relevant information
    buy_ratings = len([rating for rating in analyst_ratings if rating["rating"] == "Buy"])
    neutral_ratings = len([rating for rating in analyst_ratings if rating["rating"] == "Neutral"])
    # Process remaining sentiment data (hold, sell, etc.) as needed

    # Add analyst data to your data
    combined_data["Buy Ratings"] = buy_ratings
    combined_data["Neutral Ratings"] = neutral_ratings

    # Get analyst price targets from IEX Cloud
    analyst_target_data = client.analyst_estimates(ticker)

    # Calculate consensus price target
    consensus_target = sum(target["targetPrice"] for target in analyst_target_data) / len(analyst_target_data)

    return consensus_target


def five_year_growth():
    # Calculate start date for 5 years ago
    five_years_ago = datetime.datetime.today() - timedelta(days=365 * 5)

    # Update historical data timeframe
    hist_data = yf.download(ticker, start=five_years_ago, end=end_date)

    return hist_data


def caclulate_cagr():

    # Formula for CAGR
    cagr = (np.power(combined_data["Close"][-1] / combined_data["Close"][0], 1 / (len(hist_data) / 365)) - 1) * 100

    return cagr


def cacluate_fcf():

    operating_cash_flow = math.nan

    # Get capital expenditures data (can be from financial statements or API)
    capital_expenditures = client.key_stats(ticker, stat="capitalexpenditures")["capitalexpenditures"]

    # Calculate free cash flow
    free_cash_flow = operating_cash_flow - capital_expenditures

    return free_cash_flow


def track_news(ticker, api_key, max_articles=5):
    """
    Tracks news articles related to a specific ticker symbol.

    Args:
      ticker: The stock ticker symbol.
      api_key: News API key.
      max_articles: Maximum number of articles to return (default: 5).

    Returns:
      A list of dictionaries containing news article information.

    Raises:
      ValueError: If the ticker symbol or API key is invalid.
    """

    if not ticker or not api_key:
        raise ValueError("Missing required parameter: ticker or api_key")

    logging.info(f"Tracking news for ticker: {ticker}")

    # Initialize News API client
    newsapi = NewsApiClient(api_key)

    # Define search parameters
    query = f"{ticker} OR ({ticker} stock)"
    from_published_date = datetime.today().strftime("%Y-%m-%d")

    # Get news articles
    try:
        articles = newsapi.get_top_headlines(
            q=query,
            language="en",
            from_published_date=from_published_date,
            sort_by="publishedAt",
            page_size=max_articles,
        )
    except Exception as e:
        logging.error(f"News API error: {e}")
        return None

    # Process and return articles
    if not articles["articles"]:
        logging.info("No news articles found for this ticker.")
        return None

    return [
        {
            "title": article["title"],
            "source": article["source"]["name"],
            "url": article["url"],
            "published_date": parse(article["publishedAt"]).strftime("%Y-%m-%d"),
        }
        for article in articles["articles"]
    ][:max_articles]

def visualize_price_and_performance(combined_data):
    """
    Visualizes price and performance data using Matplotlib.

    Args:
        combined_data: A pandas DataFrame containing historical price data,
                      YTD return, and other relevant metrics.
    """

    # Create a figure and subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

    # Plot historical price trends
    ax1.plot(combined_data.index, combined_data["Close"], label="Close Price")
    ax1.set_title("Historical Price Trends")
    ax1.set_ylabel("Price")
    ax1.legend()

    # Plot YTD return and consensus price target
    ax2.bar("YTD Return", combined_data["YTD Return"], color="green")
    ax2.bar("Consensus Target", combined_data["Consensus Price Target"], color="orange")
    ax2.set_title("YTD Performance and Price Target")
    ax2.set_ylabel("% Return")

    # Customize and display the plot
    plt.tight_layout()
    plt.show()

def analyze_sentiment(text, **kwargs):
  """
  Analyzes the sentiment of a text snippet using TextBlob.

  Args:
    text: The text string to analyze.
    **kwargs: Additional arguments for TextBlob (e.g., language).

  Returns:
    A tuple containing the polarity and subjectivity scores.

  Note: Polarity ranges from -1 (negative) to 1 (positive) and subjectivity from 0 (objective) to 1 (subjective).
  """

  analysis = TextBlob(text, **kwargs)
  return analysis.sentiment.polarity, analysis.sentiment.subjectivity

def track_yahoo_sentiment(ticker, max_conversations=10):
    """
    Tracks and analyzes sentiment of Yahoo Finance conversations for a ticker.

    Args:
        ticker: The stock ticker symbol.
        max_conversations: Maximum number of conversations to analyze (default: 10).

    Returns:
        A list of dictionaries containing conversation snippets and sentiment scores.
    """

    url = f"https://finance.yahoo.com/quote/{ticker}/conversations?start={max_conversations}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    conversations = []
    for message in soup.find_all("div", class_="msg-box__content"):
        text = message.text.strip()
        if text:
            conversations.append(text)

    sentiment_data = []
    for conversation in conversations:
        polarity, subjectivity = analyze_sentiment(conversation)
        sentiment_data.append({
            "text": conversation,
            "polarity": polarity,
            "subjectivity": subjectivity,
        })

    return sentiment_data
