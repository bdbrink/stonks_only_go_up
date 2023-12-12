import yfinance as yf
from iexcloud import IEXCloud
import finnhub

# Define ticker and date range for historical data
ticker = "AMZN"
start_date = datetime.datetime(2023, 10, 1)
end_date = datetime.datetime(2023, 12, 11)
# Initialize Finnhub client
finnhub_client = finnhub.Client()

# Get historical data from Yahoo
hist_data = yf.download(ticker, start=start_date, end=end_date)

client = IEXCloud(api_token)
quote = client.quote(ticker)

# Combine historical data with real-time quote
combined_data = hist_data.append(quote.to_frame().transpose())

# Calculate YTD performance
ytd_start_date = datetime.datetime(2023, 1, 1)
ytd_return = (combined_data["Close"][-1] - combined_data["Close"][0]) / combined_data["Close"][0] * 100

# Add YTD performance to your data
combined_data["YTD Return"] = ytd_return

analyst_recommendations = finnhub_client.recommendation(symbol=ticker, verbose=False)
analyst_ratings = finnhub_client.analyst_ratings(symbol=ticker, verbose=False)

# Extract relevant information
buy_ratings = len([rating for rating in analyst_ratings if rating["rating"] == "Buy"])
neutral_ratings = len([rating for rating in analyst_ratings if rating["rating"] == "Neutral"])
# Process remaining sentiment data (hold, sell, etc.) as needed

# Add analyst data to your data
combined_data["Buy Ratings"] = buy_ratings
combined_data["Neutral Ratings"] = neutral_ratings