import yfinance as yf
from iexcloud import IEXCloud
import datetime
import finnhub

# Define ticker and date range for historical data
ticker = "AMZN"
start_date = datetime.datetime(2023, 10, 1)
end_date = datetime.datetime(2023, 12, 11)
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
    ytd_start_date = datetime.datetime(2023, 1, 1)
    ytd_return = (combined_data["Close"][-1] - combined_data["Close"][0]) / combined_data["Close"][0] * 100

    # Add YTD performance to your data
    combined_data["YTD Return"] = ytd_return

    return combined_data

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

    # Add consensus price target to your data
    combined_data["Consensus Price Target"] = consensus_target

    return consensus_target

def five_year_growth():
    # Calculate start date for 5 years ago
    five_years_ago = datetime.datetime.today() - timedelta(days=365*5)

    # Update historical data timeframe
    hist_data = yf.download(ticker, start=five_years_ago, end=end_date)

    return hist_data

