from typing import Tuple, Optional
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
        _, p_value, _ = coint(self.series1, self.series2)
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