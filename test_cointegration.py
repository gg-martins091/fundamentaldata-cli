import yfinance as yf
import pandas as pd
import os
import argparse
from modules.cointegration import CointegrationAnalyzer
import matplotlib.pyplot as plt
from typing import List, Tuple

# Global cache for stock data
_stock_data_cache = {}

def get_stock_data(ticker: str, start: str, end: str, debug: bool = False) -> pd.Series:
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
        if debug:
            print(f"Using cached data for {ticker} from {start} to {end}")
        return _stock_data_cache[cache_key]
    
    if debug:
        print(f"ticker: {ticker} start: {start} end: {end}")
    
    # Check if CSV exists (remove .SA suffix for filename)
    csv_filename = f"{ticker.replace('.SA', '')}.csv"
    if os.path.exists(csv_filename):
        if debug:
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
        if debug:
            print(f"Fetching {ticker} data from Yahoo Finance")
        data = yf.Ticker(ticker).history(start=start, end=end)['Close']
    
    # Cache the data
    _stock_data_cache[cache_key] = data
    return data


def analyze_pair_periods(stock1: str, stock2: str, end: str, lookback_days: int = None, plot_charts: bool = False, debug: bool = False, plot_spread: bool = False, olp: bool = False) -> dict:
    """
    Analyze a pair of stocks for cointegration.
    
    Args:
        stock1: First stock ticker (with .SA suffix)
        stock2: Second stock ticker (with .SA suffix)
        end: End date in YYYY-MM-DD format
        lookback_days: How many trading days to look back from end_date
        plot_charts: Whether to plot charts
        debug: Whether to print detailed statistics
        plot_spread: Whether to plot the spread chart
        
    Returns:
        Dictionary with cointegration analysis results
    """
    if not olp:
        print(f"\nAnalyzing {stock1} vs {stock2}")
        print("-" * 50)
    
    try:
        # Calculate the period needed
        max_period = lookback_days if lookback_days is not None else 250
        
        # Fetch data with an extended period (approximately 1.4x to account for weekends and holidays)
        # We'll trim it down to the exact number later
        calendar_days = int(max_period * 1.5)
        end_dt = pd.Timestamp(end).tz_localize('America/Sao_Paulo')
        start_dt = end_dt - pd.Timedelta(days=calendar_days)
        
        # Fetch data (will be cached internally)
        s1 = get_stock_data(stock1, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
        s2 = get_stock_data(stock2, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
        
        # Align dates
        common_dates = s1.index.intersection(s2.index)
        s1 = s1[common_dates]
        s2 = s2[common_dates]
        
        # Trim to the exact number of trading days requested
        if lookback_days is not None and len(s1) > lookback_days:
            s1 = s1[-lookback_days:]
            s2 = s2[-lookback_days:]
        
        actual_days = len(s1)
        
        # Create analyzer instance
        analyzer = CointegrationAnalyzer(
            series1=s1,
            series2=s2,
            names=(stock1.replace('.SA', ''), stock2.replace('.SA', '')),
            debug=debug
        )
        
        # Run analysis
        results = analyzer.analyze()
        
        # Print key results
        if not olp or results.get('has_position', False):
            print(f"\nCointegration Key Results:")
            print(f"Suggested Position: {results.get('suggested_position', 'N/A')}")
            print(f"Current Z-Score: {results.get('current_zscore', 'N/A')}")
            print(f"P-value: {results.get('p_value', 'N/A')}")
            print(f"Confidence Level: {results.get('confidence_level', 'N/A')}")

        # Plot analysis if requested
        if plot_charts or (not olp and results.get('has_position', False)):
            analyzer.plot()
        
        # Plot spread if requested
        if plot_spread and results.get('has_position', False):
            analyzer.plot_spread()
            
        return results
            
    except Exception as e:
        print(f"Error analyzing pair: {e}")
        return None

def analyze_all_pairs(stocks: List[str], end: str, lookback_days: int = None, plot_charts: bool = False, debug: bool = False, plot_spread: bool = False, olp: bool = False, csv_output: str = None) -> List[dict]:
    """
    Analyze all possible pairs from a list of stocks.
    
    Args:
        stocks: List of stock tickers (with .SA suffix)
        end: End date in YYYY-MM-DD format
        lookback_days: How many days to look back from end_date
        plot_charts: Whether to plot charts for each pair
        debug: Whether to print detailed statistics
        plot_spread: Whether to plot the spread chart
        olp: Whether to only log pairs with positions
        csv_output: Path to output CSV file when olp is active
        
    Returns:
        List of dictionaries with analysis results for each pair
    """
    print(f"\nAnalyzing all possible pairs from {len(stocks)} stocks")
    print(f"Total pairs to analyze: {len(stocks) * (len(stocks) - 1) // 2}")
    print("-" * 50)
    
    results = []
    csv_data = []
    
    # Analyze all possible pairs
    for i, stock1 in enumerate(stocks):
        for stock2 in stocks[i+1:]:  # This ensures we don't repeat pairs
            # Analyze this pair (get_stock_data handles caching internally)
            pair_result = analyze_pair_periods(
                stock1=stock1, 
                stock2=stock2, 
                end=end, 
                lookback_days=lookback_days,
                plot_charts=plot_charts,
                debug=debug,
                olp=olp
            )
            
            if pair_result:
                results.append({
                    'stock1': stock1,
                    'stock2': stock2,
                    'results': pair_result
                })
                
                # Add to CSV data if olp is active and there's a position
                if olp and csv_output and pair_result.get('has_position', False):
                    csv_data.append({
                        'stock1': stock1.replace('.SA', ''),
                        'stock2': stock2.replace('.SA', ''),
                        'suggested_position': pair_result.get('suggested_position', 'N/A'),
                        'current_zscore': pair_result.get('current_zscore', 'N/A'),
                        'p_value': pair_result.get('p_value', 'N/A'),
                        'confidence_level': pair_result.get('confidence_level', 'N/A'),
                        'beta': pair_result.get('beta', 'N/A')
                    })

            pair_result = analyze_pair_periods(
                stock1=stock2, 
                stock2=stock1, 
                end=end, 
                lookback_days=lookback_days,
                plot_charts=plot_charts,
                debug=debug,
                olp=olp
            )
            
            if pair_result:
                results.append({
                    'stock1': stock2,
                    'stock2': stock1,
                    'results': pair_result
                })
                
                # Add to CSV data if olp is active and there's a position
                if olp and csv_output and pair_result.get('has_position', False):
                    csv_data.append({
                        'stock1': stock2.replace('.SA', ''),
                        'stock2': stock1.replace('.SA', ''),
                        'suggested_position': pair_result.get('suggested_position', 'N/A'),
                        'current_zscore': pair_result.get('current_zscore', 'N/A'),
                        'p_value': pair_result.get('p_value', 'N/A'),
                        'confidence_level': pair_result.get('confidence_level', 'N/A'),
                        'beta': pair_result.get('beta', 'N/A')
                    })
    
    # Write to CSV if olp is active and csv_output is provided
    if olp and csv_output and csv_data:
        import csv
        with open(csv_output, 'w', newline='') as csvfile:
            fieldnames = ['stock1', 'stock2', 'suggested_position', 'current_zscore', 'p_value', 'confidence_level', 'beta']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
        print(f"\nCointegration results with positions saved to {csv_output}")
    
    return results


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Analyze stock pairs for cointegration')
    parser.add_argument('--debug', action='store_true', help='Print detailed statistics')
    parser.add_argument('--plot-spread', action='store_true', help='Plot the spread chart')
    parser.add_argument('--plot', action='store_true', help='Plot z-score chart for analyzed pairs')
    parser.add_argument('-olp', action='store_true', help='Only logs pairs with position')
    parser.add_argument('--only-log-positions', action='store_true', help='Only logs pairs with position')
    parser.add_argument('--csv-output', dest='csv_output', type=str, help='Output cointegration results to a CSV file when positions found')
    parser.add_argument('--period', type=int, default=200, help='Number of trading days to analyze (default: 200)')
    parser.add_argument('-p', type=int, dest='period', help='Number of trading days to analyze (shorthand for --period)')
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # List of stocks to analyze
    brazilian_stocks = [
        'VALE3.SA',
        'WEGE3.SA',
        'PETR4.SA',
        'ABEV3.SA',
        'ITUB4.SA',
        'BBAS3.SA',
        'BBDC4.SA',
        'RADL3.SA',
        'B3SA3.SA',
        'LREN3.SA',
        'BPAC11.SA',
        'VIVT3.SA',
        'EMBR3.SA',
        'IRBR3.SA',
        'VBBR3.SA',
        'HAPV3.SA',
        'CSAN3.SA',
        'SUZB3.SA',
        'PETR3.SA',
        'ELET3.SA',
        'PRIO3.SA',
        'GGBR4.SA',
        'SBSP3.SA',
        'RENT3.SA',
        'RAIL3.SA',
        'NTCO3.SA',
        'TIMS3.SA',
        'EQTL3.SA',
        'BRFS3.SA',
        'ITSA4.SA',
        'MGLU3.SA',
        'CCRO3.SA',
        'CSNA3.SA',
        'KLBN11.SA',
        'JBSS3.SA',
        'BBSE3.SA',
        'AZUL4.SA',
        'TOTS3.SA',
        'MULT3.SA',
        'MRVE3.SA',
        'ASAI3.SA',
        'MRFG3.SA',
        'CPLE6.SA',
        'RDOR3.SA',
        'UGPA3.SA',
        'ONCO3.SA',
        'CMIG4.SA',
        'BBDC3.SA',
        'ENEV3.SA',
        'IGTI11.SA',
        'CRFB3.SA',
        'VIVA3.SA',
        'STBP3.SA',
        'BRAV3.SA',
        'HYPE3.SA',
        'AZZA3.SA',
        #'PSSA3.SA',
        'SLCE3.SA',
        'ENGI11.SA',
        'AURE3.SA',
        'CPFE3.SA',
        'GOAU4.SA',
        'POMO4.SA',
        'CYRE3.SA',
    ]
    
    # EXAMPLE 1: Analyze a single pair using lookback period
    # analyze_pair_periods(
    #     stock1='CPFE3.SA',
    #     stock2='BBAS3.SA',
    #     end='2025-02-27',
    #     lookback_days=200,
    #     plot_charts=args.plot,
    #     debug=args.debug,
    #     plot_spread=args.plot_spread
    # )

    # analyze_pair_periods(
    #     stock1='BBAS3.SA',
    #     stock2='CPFE3.SA',
    #     end='2025-02-27',
    #     lookback_days=200,
    #     plot_charts=args.plot,
    #     debug=args.debug,
    #     plot_spread=args.plot_spread
    #     olp=args.olp or args.only_log_positions
    # )
    # analyze_pair_periods(
    #     stock1='CCRO3.SA',
    #     stock2='EQTL3.SA',
    #     end='2025-02-27',
    #     lookback_days=200,
    #     plot_charts=args.plot,
    #     debug=args.debug,
    #     plot_spread=args.plot_spread,
    #     olp=args.olp or args.only_log_positions
    # )
  
    # EXAMPLE 3: Analyze all possible pairs from a list of stocks
    analyze_all_pairs(
        stocks=brazilian_stocks,  # Just use the first 2 stocks for this example
        # stocks=['BBAS3.SA', 'CPFE3.SA'],
        end='2025-02-28',
        lookback_days=args.period,
        plot_charts=args.plot,
        debug=args.debug,
        plot_spread=args.plot_spread,
        olp=args.olp or args.only_log_positions,
        csv_output=args.csv_output
    )
    
    
