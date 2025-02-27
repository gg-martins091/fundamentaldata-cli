from typing import Tuple, Optional, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, coint
from sklearn.linear_model import LinearRegression
#import seaborn as sns

class CointegrationAnalyzer:
    def __init__(self, series1: pd.Series, series2: pd.Series, names: Tuple[str, str] = ('Series 1', 'Series 2'), transform_type='simple', debug: bool = False):
        """
        Initialize the cointegration analyzer with two price series.
        
        Args:
            series1: First price series
            series2: Second price series
            names: Names of the two series for plotting/display
            transform_type: Type of transformation to apply ('simple', 'exponential', or 'arithmetic')
            debug: Whether to print detailed statistics
        """
        # Store original series
        self.original_series1 = series1
        self.original_series2 = series2
        self.names = names
        self.transform_type = transform_type
        self.debug = debug
        
        # Apply transformations immediately
        self.series1, self.series2 = self.transform_series()
        # Other initializations
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

        # Run cointegration test
        self.is_cointegrated, self.p_value = self.test_cointegration()
        
        # Calculate spread and z-score
        self.spread = self.calculate_spread()
        self.zscore = self.calculate_zscore()
        
        # Print spread statistics only if in debug mode
        if self.debug:
            self.print_spread_stats()
        
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
        
        if self.debug:
            print(f"\nAugmented Dickey-Fuller Test Results: ({self.names[0]} vs {self.names[1]})")
            print(f"ADF Statistic: {adf_result[0]}")
            print(f"P-value: {adf_result[1]}")
            print("Critical values:")
            for key, value in adf_result[4].items():
                print(f"\t{key}: {value}")
        
        # Run cointegration test
        coint_t, p_value, crit_value = coint(self.series1, self.series2)
        is_cointegrated = p_value < 0.09
        
        if self.debug:
            print(f"\nCointegration Test Results: ({self.names[0]} vs {self.names[1]})")
            print(f"Cointegration t-stat: {coint_t}")
            print(f"P-value: {p_value}")
            print(f"Critical values: {crit_value}")
            print(f"Beta: {self.beta}")
            print(f"is_cointegrated: {is_cointegrated}")
        
        return is_cointegrated, p_value
        
    def calculate_spread(self) -> pd.Series:
        """
        Calculate the spread between the two series using linear regression.
        
        Returns:
            Series containing the spread values
        """
        if self.transform_type == 'arithmetic':
            # For arithmetic, the spread is already the ratio deviation from mean
            spread = self.series2 - self.series2.mean()
            self.beta = 1.0  # No regression coefficient needed for ratio approach
        else:
            # For 'simple' and 'exponential', use linear regression
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
                'message': 'Series are not cointegrated',
                'current_zscore': self.zscore.iloc[-1] if self.zscore is not None else None,
                'suggested_position': self._suggest_position()
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

    def print_spread_stats(self) -> None:
        """
        Print relevant statistics about the spread.
        """
        if self.spread is None:
            self.spread = self.calculate_spread()
            
        print(f"\nSpread Statistics:")
        print(f"Standard Deviation: {self.spread.std():.4f}")
        print(f"Current Spread: {self.spread.iloc[-1]:.4f}")
        print(f"Current Z-Score: {self.zscore.iloc[-1]:.4f}")
        print(f"Beta: {self.beta:.4f}")

    def plot_residuals(self) -> None:
        """
        Plot the standardized residuals (z-scores) with mean and ±2σ bands.
        Shows trading signal thresholds and mean-reversion visualization.
        """
        if self.spread is None:
            print("Cannot plot residuals: Series not analyzed")
            return
            
        if self.zscore is None:
            self.zscore = self.calculate_zscore()
        
        plt.figure(figsize=(12, 6))
        
        # Plot standardized residuals (z-scores)
        plt.plot(self.zscore, color='black', label='Standardized Residuals')
        
        # Plot mean line (which is zero for z-scores)
        plt.axhline(y=0, color='red', linestyle='--', label='Mean')
        
        # Plot ±2σ bands (which are at +2 and -2 for z-scores)
        plt.axhline(y=2, color='blue', linestyle='--', label='±2σ Bands')
        plt.axhline(y=-2, color='blue', linestyle='--')
        
        plt.title(f"Standardized Residuals: {self.names[0]} vs {self.names[1]} | {self.transform_type} | {self.original_series1.size} days | {self.zscore.iloc[-1]:.2f}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def transform_series(self):
        """Transform the series based on the specified transformation type"""
        if self.transform_type == 'exponential':
            raise ValueError("Exponential transformation is not supported")
        elif self.transform_type == 'arithmetic':
            raise ValueError("Arithmetic transformation is not supported")
        else:  # 'simple' or default
            transformed1 = self.original_series1
            transformed2 = self.original_series2
        
        return transformed1, transformed2 