import yfinance as yf
import pandas as pd
from modules.cointegration import CointegrationAnalyzer
import matplotlib.pyplot as plt

# Fetch data for Brazilian banks (Banco do Brasil and Itaú)
bbas = yf.Ticker("BBAS3.SA")
itub = yf.Ticker("ITUB4.SA")

# Get historical data for the last 2 years
bbas_data = bbas.history(period="2y")['Close']
itub_data = itub.history(period="2y")['Close']

# Make sure both series have the same dates
common_dates = bbas_data.index.intersection(itub_data.index)
bbas_data = bbas_data[common_dates]
itub_data = itub_data[common_dates]

# Create analyzer instance
analyzer = CointegrationAnalyzer(
    series1=bbas_data,
    series2=itub_data,
    names=('BBAS3', 'ITUB4')
)

# Run analysis
results = analyzer.analyze()

# Print results
print("\nCointegration Analysis Results:")
print("-" * 30)
for key, value in results.items():
    print(f"{key}: {value}")

# Plot the analysis
analyzer.plot()
plt.show() 