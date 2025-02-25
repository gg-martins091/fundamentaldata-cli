import yfinance as yf
import pandas as pd
import os
from modules.cointegration import CointegrationAnalyzer
import matplotlib.pyplot as plt
from typing import List

def get_stock_data(ticker: str, start: str, end: str) -> pd.Series:
    """
    Get stock data from either CSV file (if exists) or Yahoo Finance.
    
    Args:
        ticker: Stock ticker (with .SA suffix)
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        
    Returns:
        Series containing stock prices
    """
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
        return df.loc[mask]['Close']
    
    print(f"Fetching {ticker} data from Yahoo Finance")
    return yf.Ticker(ticker).history(start=start, end=end)['Close']

def analyze_pair(stock1: str, stock2: str, start: str = "2019-07-01", end: str = "2020-02-25") -> None:
    """
    Analyze a pair of stocks for cointegration.
    
    Args:
        stock1: First stock ticker (with .SA suffix)
        stock2: Second stock ticker (with .SA suffix)
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
    """
    print(f"\nAnalyzing {stock1} vs {stock2}")
    print("-" * 50)
    
    # Fetch data
    try:
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
        # if results['is_cointegrated']:
        print(f"✓ Cointegrated pair found!")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Plot analysis for cointegrated pairs
        analyzer.plot()
        analyzer.plot_residuals()
        # else:
        #     print(f"✗ Not cointegrated (p-value: {results['p_value']:.4f})")
            
    except Exception as e:
        print(f"Error analyzing pair: {e}")


def analyze_pair_periods(stock1: str, stock2: str, end: str, periods: List[int], lookback_days: int = None) -> None:
    """
    Analyze a pair of stocks for cointegration using multiple window sizes.
    
    Args:
        stock1: First stock ticker (with .SA suffix)
        stock2: Second stock ticker (with .SA suffix)
        end: End date in YYYY-MM-DD format
        periods: List of window sizes in days for rolling analysis
        lookback_days: How many days to look back from end_date. If None, uses max(periods)
    """
    print(f"\nAnalyzing {stock1} vs {stock2} with multiple periods")
    print("-" * 50)
    
    try:
        # Calculate the period needed
        max_period = lookback_days if lookback_days is not None else max(periods)
        end_dt = pd.Timestamp(end).tz_localize('America/Sao_Paulo')
        start_dt = end_dt - pd.Timedelta(days=max_period)
        
        # Fetch data
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
        
        # Plot multi-period analysis
        analyzer.plot_residuals_multi_period(end_dt, periods, lookback_days)
            
    except Exception as e:
        print(f"Error analyzing pair: {e}")

def analyze_all_pairs(stocks: List[str], end: str, periods: List[int], lookback_days: int = None, plot_charts: bool = False) -> None:
    """
    Analyze all possible pairs from a list of stocks.
    Caches stock data to avoid multiple API calls.
    
    Args:
        stocks: List of stock tickers (with .SA suffix)
        end: End date in YYYY-MM-DD format
        periods: List of window sizes in days for rolling analysis
        lookback_days: How many days to look back from end_date
        plot_charts: Whether to plot charts for each pair
    """
    print(f"\nAnalyzing all possible pairs from {len(stocks)} stocks")
    print(f"Total pairs to analyze: {len(stocks) * (len(stocks) - 1) // 2}")
    print("-" * 50)
    
    # Setup dates
    end_dt = pd.Timestamp(end).tz_localize('America/Sao_Paulo')
    max_period = lookback_days if lookback_days is not None else max(periods)
    start_dt = end_dt - pd.Timedelta(days=max_period)
    
    # Cache for stock data
    stock_data = {}
    
    # Fetch and cache all stock data
    print("Fetching stock data...")
    for stock in stocks:
        try:
            data = get_stock_data(stock, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
            stock_data[stock] = data
            print(f"✓ {stock} data fetched")
        except Exception as e:
            print(f"✗ Error fetching {stock}: {e}")
            stock_data[stock] = None
    
    # Analyze all possible pairs
    for i, stock1 in enumerate(stocks):
        for stock2 in stocks[i+1:]:  # This ensures we don't repeat pairs
            if stock_data[stock1] is None or stock_data[stock2] is None:
                print(f"Skipping {stock1} vs {stock2} due to missing data")
                continue
                
            print(f"\nAnalyzing {stock1} vs {stock2}")
            print("-" * 30)
            try:
                # Align dates
                common_dates = stock_data[stock1].index.intersection(stock_data[stock2].index)
                s1 = stock_data[stock1][common_dates]
                s2 = stock_data[stock2][common_dates]
                
                # Create analyzer instance
                analyzer = CointegrationAnalyzer(
                    series1=s1,
                    series2=s2,
                    names=(stock1.replace('.SA', ''), stock2.replace('.SA', ''))
                )
                
                # Run analysis and print stats
                results = analyzer.analyze()
                analyzer.print_spread_stats()
                
                # Plot only if requested
                if plot_charts:
                    analyzer.plot_residuals_multi_period(end_dt, periods, lookback_days)
                
            except Exception as e:
                print(f"Error analyzing pair: {e}")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Example of multi-period analysis with extended lookback
    analyze_pair_periods('RENT3.SA', 'EMBR3.SA', 
                        end='2025-02-25',
                        periods=[120],
                        lookback_days=250)  # Look back 250 days but analyze windows of 120 and 160 days
    plt.show()
    
    # List of stocks to analyze
    # brazilian_stocks = [
    #     'VALE3.SA',
    #     'PETR4.SA',
    #     'ITUB4.SA',
    #     'BBAS3.SA',
    #     'B3SA3.SA',
    #     'LREN3.SA',
    #     'WEGE3.SA',
    #     'ELET3.SA',
    #     'ABEV3.SA',
    #     'CSAN3.SA',
    #     'EMBR3.SA',
    #     'RENT3.SA'
    # ]
    
    # # Analyze all possible pairs without plotting
    # analyze_all_pairs(
    #     stocks=brazilian_stocks,
    #     end='2025-02-25',
    #     periods=[120],
    #     lookback_days=250,
    #     plot_charts=True  # Set to True if you want to see the charts
    # )
    # plt.show() 