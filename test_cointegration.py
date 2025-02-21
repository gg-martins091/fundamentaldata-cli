import yfinance as yf
import pandas as pd
from modules.cointegration import CointegrationAnalyzer
import matplotlib.pyplot as plt

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
        s1 = yf.Ticker(stock1).history(start=start, end=end)['Close']
        s2 = yf.Ticker(stock2).history(start=start, end=end)['Close']
        
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

def test_brazilian_pairs():
    """
    Test predefined Brazilian stock pairs for cointegration.
    Pairs are grouped by sector for better analysis.
    """
    # Banks
    bank_pairs = [
        ('BBAS3.SA', 'ITUB4.SA'),  # Banco do Brasil vs Itaú
        ('ITUB4.SA', 'BBAS3.SA'),  # Itaú vs Banco do Brasil
        ('BBDC4.SA', 'ITUB4.SA'),  # Bradesco vs Itaú
        ('BBAS3.SA', 'BBDC4.SA'),  # Banco do Brasil vs Bradesco
        ('SANB11.SA', 'ITUB4.SA'), # Santander vs Itaú
    ]
    
    # Oil & Gas
    oil_pairs = [
        ('PETR3.SA', 'PETR4.SA'),  # Petrobras ON vs PN
        ('PRIO3.SA', 'PETR4.SA'),  # PetroRio vs Petrobras
    ]
    
    # Mining & Steel
    mining_pairs = [
        ('VALE3.SA', 'CSNA3.SA'),  # Vale vs CSN
        ('GGBR4.SA', 'CSNA3.SA'),  # Gerdau vs CSN
    ]
    
    # Retail
    retail_pairs = [
        ('PCAR3.SA', 'SMAL11.SA'),  # PCAR4 vs SMALL11
        ('SMAL11.SA', 'PCAR3.SA'),  # PCAR4 vs SMALL11
        ('MGLU3.SA', 'VIIA3.SA'),  # Magazine Luiza vs Via Varejo
        ('LREN3.SA', 'ARZZ3.SA'),  # Renner vs Arezzo
    ]
    
    # Electric
    electric_pairs = [
        ('CMIG4.SA', 'ELET6.SA'),  # Cemig vs Eletrobras
        ('ENGI11.SA', 'ELET6.SA'), # Energisa vs Eletrobras
    ]
    
    # Test all pairs
    all_pairs = {
        'Retail': retail_pairs,
        'Banks': bank_pairs,
        'Oil & Gas': oil_pairs,
        'Mining & Steel': mining_pairs,
        'Electric': electric_pairs
    }
    
    for sector, pairs in all_pairs.items():
        print(f"\n=== Testing {sector} Sector ===")
        for stock1, stock2 in pairs:
            analyze_pair(stock1, stock2)

if __name__ == "__main__":
    # test_brazilian_pairs()
    # analyze_pair('CYRE3.SA', 'CCRO3.SA', start='2023-12-18', end='2024-08-05')
    analyze_pair('CCRO3.SA', 'CYRE3.SA', start='2023-12-18', end='2024-08-05')
    plt.show() 