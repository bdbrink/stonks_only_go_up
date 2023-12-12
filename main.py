import yfinance as yf
from iexcloud import IEXCloud

# Define ticker and date range for historical data
ticker = "AMZN"
start_date = datetime.datetime(2023, 10, 1)
end_date = datetime.datetime(2023, 12, 11)

# Get historical data from Yahoo
hist_data = yf.download(ticker, start=start_date, end=end_date)

# Get real-time quote from IEX Cloud (requires API key)
client = IEXCloud(api_token="YOUR_API_KEY")
quote = client.quote(ticker)

# Combine historical data with real-time quote
combined_data = hist_data.append(quote.to_frame().transpose())

# Calculate YTD performance
ytd_start_date = datetime.datetime(2023, 1, 1)
ytd_return = (combined_data["Close"][-1] - combined_data["Close"][0]) / combined_data["Close"][0] * 100

# Add YTD performance to your data
combined_data["YTD Return"] = ytd_return