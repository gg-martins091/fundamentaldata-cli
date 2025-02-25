from typing import Tuple, Optional, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, coint
from sklearn.linear_model import LinearRegression
#import seaborn as sns

class CointegrationAnalyzer:
    def __init__(self, series1: pd.Series, series2: pd.Series, names: Tuple[str, str] = ('Series 1', 'Series 2')):
        """
        Initialize the cointegration analyzer with two price series.
        
        Args:
            series1: First price series
            series2: Second price series
            names: Names of the two series for plotting/display
        """
        self.series1 = series1
        self.series2 = series2
        self.names = names
        self.spread = None
        self.beta = None
        self.is_cointegrated = None
        self.p_value = None
        self.zscore = None
        
    def analyze(self) -> dict:
        """
        Perform complete cointegration analysis.
        
        Returns:
            Dictionary containing analysis results
        """

        # print(f"series1: {self.series1}")   
        # print(f"series2: {self.series2}")
        # self.series1.iloc[::-1].to_csv('series1.csv')
        # self.series2.iloc[::-1].to_csv('series2.csv')
        # Run cointegration test
        self.is_cointegrated, self.p_value = self.test_cointegration()
        
        # Calculate spread and z-score
        self.spread = self.calculate_spread()
        self.zscore = self.calculate_zscore()
        
        return self.get_summary_stats()
        
    def test_cointegration(self) -> Tuple[bool, float]:
        """
        Test if the two series are cointegrated using the Engle-Granger method.
        
        Returns:
            Tuple containing:
            - Boolean indicating if series are cointegrated
            - P-value of the cointegration test
        """
        # Run Dickey-Fuller test on spread
        spread = self.calculate_spread()
        adf_result = adfuller(spread)
        print("\nAugmented Dickey-Fuller Test Results:")
        print(f"ADF Statistic: {adf_result[0]}")
        print(f"P-value: {adf_result[1]}")
        print("Critical values:")
        for key, value in adf_result[4].items():
            print(f"\t{key}: {value}")
        
        # Run cointegration test
        coint_t, p_value, crit_value = coint(self.series1, self.series2)
        print(f"\nCointegration Test Results:")
        print(f"Cointegration t-stat: {coint_t}")
        print(f"P-value: {p_value}")
        print(f"Critical values: {crit_value}")
        print(f"Beta: {self.beta}")
        print(f"is_cointegrated: {p_value < 0.05}")
        
        return p_value < 0.05, p_value
        
    def calculate_spread(self) -> pd.Series:
        """
        Calculate the spread between the two series using linear regression.
        
        Returns:
            Series containing the spread values
        """
        # Reshape for sklearn
        X = self.series1.values.reshape(-1, 1)
        y = self.series2.values
        
        # Fit linear regression
        reg = LinearRegression()
        reg.fit(X, y)
        self.beta = reg.coef_[0]
        
        # Calculate spread
        spread = self.series2 - (self.beta * self.series1)
        return spread
        
    def calculate_zscore(self) -> pd.Series:
        """
        Calculate the z-score of the spread.
        
        Returns:
            Series containing z-scores
        """
        if self.spread is None:
            self.spread = self.calculate_spread()
            
        zscore = (self.spread - self.spread.mean()) / self.spread.std()
        return zscore

    def get_summary_stats(self) -> dict:
        """
        Get summary statistics of the cointegration analysis.
        
        Returns:
            Dictionary containing summary statistics
        """
        if not self.is_cointegrated:
            return {
                'is_cointegrated': False,
                'p_value': self.p_value,
                'message': 'Series are not cointegrated'
            }

        return {
            'is_cointegrated': self.is_cointegrated,
            'p_value': self.p_value,
            'beta': self.beta,
            'spread_mean': self.spread.mean(),
            'spread_std': self.spread.std(),
            'current_zscore': self.zscore.iloc[-1],
            'suggested_position': self._suggest_position()
        }
    
    def _suggest_position(self) -> str:
        """
        Suggest trading position based on current z-score.
        """
        if self.zscore is None:
            return "No position - series not analyzed"
            
        current_zscore = self.zscore.iloc[-1]
        
        if current_zscore > 2:
            return f"Short {self.names[1]}, Long {self.beta:.2f}x {self.names[0]}"
        elif current_zscore < -2:
            return f"Long {self.names[1]}, Short {self.beta:.2f}x {self.names[0]}"
        else:
            return "No position - spread within normal range"
    
    def plot(self, show_signals: bool = True) -> None:
        """
        Plot the analysis results.
        
        Args:
            show_signals: Whether to show trading signal zones
        """
        self.plot_residuals()
        return
        
        if not self.is_cointegrated:
            plt.figure(figsize=(10, 6))
            plt.plot(self.series1, label=self.names[0])
            plt.plot(self.series2, label=self.names[1])
            plt.title("Non-cointegrated Series")
            plt.legend()
            plt.show()
            return
            
        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Plot original series
        ax1.plot(self.series1, label=self.names[0])
        ax1.plot(self.series2, label=self.names[1])
        ax1.set_title("Original Series")
        ax1.legend()
        
        # Plot spread
        ax2.plot(self.spread)
        ax2.axhline(y=0, color='r', linestyle='--')
        ax2.set_title("Spread")
        
        # Plot z-score
        ax3.plot(self.zscore)
        if show_signals:
            ax3.axhline(y=0, color='r', linestyle='--')
            ax3.axhline(y=2, color='g', linestyle='--', label='Entry/Exit Zones')
            ax3.axhline(y=-2, color='g', linestyle='--')
        ax3.set_title("Z-Score")
        
        plt.tight_layout()
        plt.show()

    def plot_residuals(self) -> None:
        """
        Plot the residuals (spread) with mean and ±2σ bands.
        Shows trading signal thresholds and mean-reversion visualization.
        """
        if self.spread is None:
            print("Cannot plot residuals: Series not analyzed")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Plot residuals
        plt.plot(self.spread, color='black', label='Residuals')
        
        # Plot mean line
        mean = self.spread.mean()
        plt.axhline(y=mean, color='red', linestyle='--', label='Mean')
        
        # Plot ±2σ bands
        std = self.spread.std()
        plt.axhline(y=mean + 2*std, color='blue', linestyle='--', label='±2σ Bands')
        plt.axhline(y=mean - 2*std, color='blue', linestyle='--')
        
        plt.title(f"Residuals Analysis: {self.names[0]} vs {self.names[1]}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def print_spread_stats(self) -> None:
        """
        Print relevant statistics about the spread.
        """
        if self.spread is None:
            self.spread = self.calculate_spread()
            
        print(f"Spread Statistics:")
        print(f"Standard Deviation: {self.spread.std():.4f}")
        print(f"Current Spread: {self.spread.iloc[-1]:.4f}")
        print(f"Current Z-Score: {self.zscore.iloc[-1]:.4f}")
        print(f"Beta: {self.beta:.4f}")

    def analyze_periods(self, end_date: pd.Timestamp, periods: List[int], lookback_days: int = None) -> List[dict]:
        """
        Analyze cointegration for multiple window sizes.
        
        Args:
            end_date: The end date for analysis
            periods: List of window sizes in days for rolling analysis
            lookback_days: How many days to look back from end_date. If None, uses max(periods)
            
        Returns:
            List of dictionaries containing analysis results for each period
        """
        results = []
        lookback = lookback_days if lookback_days is not None else max(periods)
        
        start_date = end_date - pd.Timedelta(days=lookback)
        
        # Get data for the entire period
        mask = (self.series1.index <= end_date) & (self.series1.index >= start_date)
        full_series1 = self.series1[mask]
        full_series2 = self.series2[mask]
        
        for window in periods:
            # Get the last 'window' days of data
            period_series1 = full_series1.iloc[-window:]
            period_series2 = full_series2.iloc[-window:]
            
            # Create temporary analyzer for this window
            period_analyzer = CointegrationAnalyzer(period_series1, period_series2, self.names)
            result = period_analyzer.analyze()
            
            # Print statistics for this window
            print(f"\nWindow Size: {window} days")
            period_analyzer.print_spread_stats()
            
            # Store results
            results.append({
                'period': window,
                'analyzer': period_analyzer,
                'results': result
            })
            
        return results

    def plot_residuals_multi_period(self, end_date: pd.Timestamp, periods: List[int], lookback_days: int = None) -> None:
        """
        Plot residuals for multiple window sizes in the same window.
        
        Args:
            end_date: The end date for analysis
            periods: List of window sizes in days for rolling analysis
            lookback_days: How many days to look back from end_date. If None, uses max(periods)
        """
        results = self.analyze_periods(end_date, periods, lookback_days)
        
        # Create figure with subplots
        fig, axes = plt.subplots(len(periods), 1, figsize=(12, 4*len(periods)))
        
        for idx, result in enumerate(results):
            window = result['period']
            analyzer = result['analyzer']
            ax = axes[idx] if len(periods) > 1 else axes
            
            # Plot residuals
            ax.plot(analyzer.spread, color='black', label='Residuals')
            
            # Plot mean line
            mean = analyzer.spread.mean()
            ax.axhline(y=mean, color='red', linestyle='--', label='Mean')
            
            # Plot ±2σ bands
            std = analyzer.spread.std()
            ax.axhline(y=mean + 2*std, color='blue', linestyle='--', label='±2σ Bands')
            ax.axhline(y=mean - 2*std, color='blue', linestyle='--')
            
            ax.set_title(f"{window} Days Window")
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle(f"Residuals Analysis: {self.names[0]} vs {self.names[1]}")
        plt.tight_layout()
        plt.show() 