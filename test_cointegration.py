import yfinance as yf
import pandas as pd
import os
from modules.cointegration import CointegrationAnalyzer
import matplotlib.pyplot as plt
from typing import List, Tuple

# Global cache for stock data
_stock_data_cache = {}

def get_stock_data(ticker: str, start: str, end: str) -> pd.Series:
    """
    Get stock data from cache, CSV file, or Yahoo Finance.
    Automatically caches results for future calls.
    
    Args:
        ticker: Stock ticker (with .SA suffix)
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        
    Returns:
        Series containing stock prices
    """
    # Create a cache key from the parameters
    cache_key = f"{ticker}_{start}_{end}"
    
    # Check if data is already in cache
    if cache_key in _stock_data_cache:
        print(f"Using cached data for {ticker} from {start} to {end}")
        return _stock_data_cache[cache_key]
    
    print(f"ticker: {ticker} start: {start} end: {end}")
    
    # Check if CSV exists (remove .SA suffix for filename)
    csv_filename = f"{ticker.replace('.SA', '')}.csv"
    if os.path.exists(csv_filename):
        print(f"Loading {ticker} data from {csv_filename}")
        # Read CSV and ensure datetime index
        df = pd.read_csv(csv_filename, index_col=0, parse_dates=True)
        # Localize index to America/Sao_Paulo timezone
        df.index = df.index.tz_localize('America/Sao_Paulo')
        
        # Convert start and end to timezone-aware timestamps
        start_dt = pd.Timestamp(start).tz_localize('America/Sao_Paulo')
        end_dt = pd.Timestamp(end).tz_localize('America/Sao_Paulo')
        
        # Filter for the requested date range
        mask = (df.index >= start_dt) & (df.index <= end_dt)
        data = df.loc[mask]['Close']
    else:
        print(f"Fetching {ticker} data from Yahoo Finance")
        data = yf.Ticker(ticker).history(start=start, end=end)['Close']
    
    # Cache the data
    _stock_data_cache[cache_key] = data
    return data


    """
    Analyze a specific historical time range for a pair of stocks.
    
    Args:
        stock1: First stock ticker (with .SA suffix)
        stock2: Second stock ticker (with .SA suffix)
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        plot_charts: Whether to plot charts
        
    Returns:
        Dictionary with cointegration analysis results
    """
    print(f"\nAnalyzing {stock1} vs {stock2} from {start} to {end}")
    print("-" * 50)
    
    try:
        # Get specific date range data
        s1 = get_stock_data(stock1, start, end)
        s2 = get_stock_data(stock2, start, end)
        
        # Align dates
        common_dates = s1.index.intersection(s2.index)
        s1 = s1[common_dates]
        s2 = s2[common_dates]
        
        # Create analyzer instance
        analyzer = CointegrationAnalyzer(
            series1=s1,
            series2=s2,
            names=(stock1.replace('.SA', ''), stock2.replace('.SA', ''))
        )
        
        # Run analysis
        results = analyzer.analyze()
        
        # Print results
        print(f"\nCointegration Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Plot analysis if requested
        if plot_charts:
            analyzer.plot()
            analyzer.plot_residuals()
            
        return results
            
    except Exception as e:
        print(f"Error analyzing pair: {e}")
        return None

def analyze_pair_periods(stock1: str, stock2: str, end: str, lookback_days: int = None, plot_charts: bool = True) -> dict:
    """
    Analyze a pair of stocks for cointegration.
    
    Args:
        stock1: First stock ticker (with .SA suffix)
        stock2: Second stock ticker (with .SA suffix)
        end: End date in YYYY-MM-DD format
        lookback_days: How many days to look back from end_date
        plot_charts: Whether to plot charts
        
    Returns:
        Dictionary with cointegration analysis results
    """
    print(f"\nAnalyzing {stock1} vs {stock2}")
    print("-" * 50)
    
    try:
        # Calculate the period needed
        max_period = lookback_days if lookback_days is not None else 250
        end_dt = pd.Timestamp(end).tz_localize('America/Sao_Paulo')
        start_dt = end_dt - pd.Timedelta(days=max_period)
        
        # Fetch data (will be cached internally)
        s1 = get_stock_data(stock1, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
        s2 = get_stock_data(stock2, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
        
        # Align dates
        common_dates = s1.index.intersection(s2.index)
        s1 = s1[common_dates]
        s2 = s2[common_dates]
        
        # Create analyzer instance
        analyzer = CointegrationAnalyzer(
            series1=s1,
            series2=s2,
            names=(stock1.replace('.SA', ''), stock2.replace('.SA', ''))
        )
        
        # Run analysis
        results = analyzer.analyze()
        
        # Print results
        print(f"\nCointegration Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Plot analysis if requested
        if plot_charts:
            analyzer.plot()
            
        return results
            
    except Exception as e:
        print(f"Error analyzing pair: {e}")
        return None

def analyze_all_pairs(stocks: List[str], end: str, lookback_days: int = None, plot_charts: bool = False) -> List[dict]:
    """
    Analyze all possible pairs from a list of stocks.
    
    Args:
        stocks: List of stock tickers (with .SA suffix)
        end: End date in YYYY-MM-DD format
        lookback_days: How many days to look back from end_date
        plot_charts: Whether to plot charts for each pair
        
    Returns:
        List of dictionaries with analysis results for each pair
    """
    print(f"\nAnalyzing all possible pairs from {len(stocks)} stocks")
    print(f"Total pairs to analyze: {len(stocks) * (len(stocks) - 1) // 2}")
    print("-" * 50)
    
    results = []
    
    # Analyze all possible pairs
    for i, stock1 in enumerate(stocks):
        for stock2 in stocks[i+1:]:  # This ensures we don't repeat pairs
            # Analyze this pair (get_stock_data handles caching internally)
            pair_result = analyze_pair_periods(
                stock1=stock1, 
                stock2=stock2, 
                end=end, 
                lookback_days=lookback_days,
                plot_charts=plot_charts
            )
            
            if pair_result:
                results.append({
                    'stock1': stock1,
                    'stock2': stock2,
                    'results': pair_result
                })
    
    return results


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # List of stocks to analyze
    brazilian_stocks = [
        # 'VALE3.SA',   # Vale
        # 'PETR4.SA',   # Petrobras
        # 'ITUB4.SA',   # Itau Unibanco
        # 'BBAS3.SA',   # Banco do Brasil
        'EMBR3.SA',   # Embraer
        'RENT3.SA'    # Localiza
    ]
    
    # EXAMPLE 1: Analyze a single pair using lookback period
    # analyze_pair_periods(
    #     stock1='EMBR3.SA',
    #     stock2='RENT3.SA',
    #     end='2025-02-25',
    #     lookback_days=250,
    #     plot_charts=True
    # )
    
  
    
    # EXAMPLE 3: Analyze all possible pairs from a list of stocks
    analyze_all_pairs(
        stocks=brazilian_stocks,  # Just use the first 2 stocks for this example
        end='2025-02-25',
        lookback_days=250,
        plot_charts=True
    )
    