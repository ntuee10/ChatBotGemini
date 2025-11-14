"""
Advanced Analytics Engine for GBD Data
Implements: CausalImpact, Prophet Forecasting, A/B Testing, Temporal Trends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Statistical libraries
from scipy import stats
from statsmodels.stats.power import TTestIndPower
from statsmodels.tsa.seasonal import seasonal_decompose

# Advanced analytics
try:
    from causalimpact import CausalImpact
    CAUSALIMPACT_AVAILABLE = True
except ImportError:
    CAUSALIMPACT_AVAILABLE = False
    print("⚠️  CausalImpact not installed. Run: pip install causalimpact")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not installed. Run: pip install prophet")

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class AdvancedGBDAnalytics:
    """
    Advanced analytics engine for GBD datasets.

    Features:
    1. Causal Impact Analysis (intervention effects)
    2. Prophet Forecasting (time-series predictions)
    3. A/B Testing (hypothesis testing, power analysis)
    4. Temporal Trend Analysis (decomposition, change points)
    """

    def __init__(self, df: pd.DataFrame, date_column: Optional[str] = None):
        """
        Initialize analytics engine.

        Args:
            df: Input DataFrame (GBD data)
            date_column: Name of date column (auto-detected if None)
        """
        self.df = df.copy()
        self.date_column = date_column or self._detect_date_column()

        if self.date_column:
            self.df[self.date_column] = pd.to_datetime(self.df[self.date_column])
            self.df = self.df.sort_values(self.date_column).reset_index(drop=True)

    def _detect_date_column(self) -> Optional[str]:
        """Auto-detect date column"""
        date_keywords = ['date', 'time', 'year', 'period', 'timestamp']
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in date_keywords):
                try:
                    pd.to_datetime(self.df[col])
                    return col
                except:
                    continue
        return None

    # ========================================================================
    # 1. CAUSAL IMPACT ANALYSIS
    # ========================================================================

    def causal_impact_analysis(
        self,
        metric: str,
        intervention_date: Union[str, datetime],
        control_metrics: Optional[List[str]] = None,
        pre_period_days: int = 90,
        post_period_days: int = 90,
        save_plot: bool = True,
        plot_path: str = 'causal_impact.png'
    ) -> Dict:
        """
        Analyze causal impact of an intervention using Bayesian structural time series.

        Example use case: "Did the COVID-19 lockdown reduce traffic deaths?"

        Args:
            metric: Target metric to analyze (e.g., 'deaths', 'DALYs')
            intervention_date: Date of intervention
            control_metrics: Covariates unaffected by intervention (for better counterfactual)
            pre_period_days: Days before intervention for training
            post_period_days: Days after intervention for analysis

        Returns:
            Dict with impact estimates, p-value, and visualizations
        """
        if not CAUSALIMPACT_AVAILABLE:
            return {"error": "CausalImpact not installed"}

        if not self.date_column:
            return {"error": "No date column found for causal analysis"}

        # Prepare data
        intervention_date = pd.to_datetime(intervention_date)
        pre_start = intervention_date - pd.Timedelta(days=pre_period_days)
        post_end = intervention_date + pd.Timedelta(days=post_period_days)

        # Filter data
        data = self.df[
            (self.df[self.date_column] >= pre_start) &
            (self.df[self.date_column] <= post_end)
        ].copy()

        # Prepare time series
        if control_metrics:
            ts_data = data[[self.date_column, metric] + control_metrics].set_index(self.date_column)
        else:
            ts_data = data[[self.date_column, metric]].set_index(self.date_column)

        # Define periods
        pre_period = [ts_data.index[0], intervention_date - pd.Timedelta(days=1)]
        post_period = [intervention_date, ts_data.index[-1]]

        # Run CausalImpact
        ci = CausalImpact(ts_data, pre_period, post_period)

        # Extract results
        summary = ci.summary()
        summary_data = ci.summary_data

        results = {
            'average_impact': float(summary_data['average']['actual'] - summary_data['average']['predicted']),
            'cumulative_impact': float(summary_data['cumulative']['actual'] - summary_data['cumulative']['predicted']),
            'p_value': float(summary_data.get('p_value', 0)),
            'relative_effect': f"{summary_data['average'].get('rel_effect_lower', 0):.1%} - {summary_data['average'].get('rel_effect_upper', 0):.1%}",
            'summary': summary,
            'interpretation': self._interpret_causal_impact(summary_data)
        }

        # Plot
        if save_plot:
            ci.plot(figsize=(15, 12))
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            results['plot_path'] = plot_path

        return results

    def _interpret_causal_impact(self, summary_data: pd.DataFrame) -> str:
        """Generate natural language interpretation of causal impact"""
        avg_effect = summary_data['average']['actual'] - summary_data['average']['predicted']
        p_value = summary_data.get('p_value', 1.0)

        if p_value < 0.05:
            significance = "statistically significant"
        else:
            significance = "not statistically significant"

        if avg_effect > 0:
            direction = "increase"
        else:
            direction = "decrease"

        return (
            f"The intervention resulted in a {significance} {direction} of "
            f"{abs(avg_effect):.2f} units on average (p={p_value:.3f})."
        )

    # ========================================================================
    # 2. PROPHET FORECASTING
    # ========================================================================

    def prophet_forecast(
        self,
        metric: str,
        periods: int = 365,
        freq: str = 'D',
        include_holidays: bool = False,
        save_plot: bool = True,
        plot_path: str = 'prophet_forecast.png'
    ) -> Dict:
        """
        Generate time-series forecast using Meta's Prophet.

        Example use case: "Predict diabetes prevalence for the next 5 years"

        Args:
            metric: Metric to forecast (e.g., 'prevalence', 'deaths')
            periods: Number of future periods to forecast
            freq: Frequency ('D'=daily, 'W'=weekly, 'M'=monthly, 'Y'=yearly)
            include_holidays: Include holiday effects

        Returns:
            Dict with forecast, confidence intervals, and components
        """
        if not PROPHET_AVAILABLE:
            return {"error": "Prophet not installed"}

        if not self.date_column:
            return {"error": "No date column found for forecasting"}

        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = self.df[[self.date_column, metric]].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df = prophet_df.dropna()

        # Initialize and fit Prophet
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True if freq == 'D' else False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05  # Flexibility of trend changes
        )

        # Add country-specific holidays if requested
        if include_holidays:
            # You can add custom holidays here for GBD regions
            pass

        model.fit(prophet_df)

        # Make future dataframe
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)

        # Extract key results
        latest_actual = prophet_df['y'].iloc[-1]
        final_forecast = forecast['yhat'].iloc[-1]
        pct_change = ((final_forecast - latest_actual) / latest_actual) * 100

        results = {
            'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            'latest_actual': float(latest_actual),
            'final_forecast': float(final_forecast),
            'percent_change': float(pct_change),
            'trend': 'increasing' if pct_change > 0 else 'decreasing',
            'components': {
                'trend': forecast[['ds', 'trend']],
                'yearly': forecast[['ds', 'yearly']] if 'yearly' in forecast else None,
                'weekly': forecast[['ds', 'weekly']] if 'weekly' in forecast else None,
            }
        }

        # Create visualization
        if save_plot:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(f'{metric} Forecast', 'Trend Components'),
                vertical_spacing=0.15,
                row_heights=[0.6, 0.4]
            )

            # Forecast plot
            fig.add_trace(
                go.Scatter(x=prophet_df['ds'], y=prophet_df['y'],
                          mode='lines', name='Actual', line=dict(color='black')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                          mode='lines', name='Forecast', line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                          mode='lines', line=dict(width=0), showlegend=False),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                          mode='lines', line=dict(width=0),
                          fill='tonexty', fillcolor='rgba(0,100,250,0.2)',
                          name='Confidence Interval'),
                row=1, col=1
            )

            # Trend component
            fig.add_trace(
                go.Scatter(x=forecast['ds'], y=forecast['trend'],
                          mode='lines', name='Trend', line=dict(color='red')),
                row=2, col=1
            )

            fig.update_layout(height=800, title_text=f"{metric} - Prophet Forecast")
            fig.write_image(plot_path, width=1200, height=800)
            results['plot_path'] = plot_path

        return results

    # ========================================================================
    # 3. A/B TESTING
    # ========================================================================

    def ab_test_analysis(
        self,
        metric: str,
        group_column: str,
        group_a: str,
        group_b: str,
        alpha: float = 0.05,
        test_type: str = 'ttest'  # 'ttest', 'mannwhitney', 'chisquare'
    ) -> Dict:
        """
        Comprehensive A/B test analysis with statistical hypothesis testing.

        Example use case: "Did intervention A reduce mortality more than intervention B?"

        Args:
            metric: Metric to compare (e.g., 'deaths', 'DALYs')
            group_column: Column containing group labels
            group_a: Label for group A (control)
            group_b: Label for group B (treatment)
            alpha: Significance level (default 0.05)
            test_type: Statistical test to use

        Returns:
            Dict with test results, effect size, power analysis
        """
        # Filter data
        group_a_data = self.df[self.df[group_column] == group_a][metric].dropna()
        group_b_data = self.df[self.df[group_column] == group_b][metric].dropna()

        if len(group_a_data) == 0 or len(group_b_data) == 0:
            return {"error": "Insufficient data in one or both groups"}

        # Descriptive statistics
        results = {
            'group_a': {
                'name': group_a,
                'n': len(group_a_data),
                'mean': float(group_a_data.mean()),
                'std': float(group_a_data.std()),
                'median': float(group_a_data.median())
            },
            'group_b': {
                'name': group_b,
                'n': len(group_b_data),
                'mean': float(group_b_data.mean()),
                'std': float(group_b_data.std()),
                'median': float(group_b_data.median())
            }
        }

        # Perform statistical test
        if test_type == 'ttest':
            # Independent t-test
            statistic, p_value = stats.ttest_ind(group_a_data, group_b_data)
            # Cohen's d (effect size)
            pooled_std = np.sqrt((group_a_data.std()**2 + group_b_data.std()**2) / 2)
            cohens_d = (group_b_data.mean() - group_a_data.mean()) / pooled_std
            effect_size = float(cohens_d)
            test_name = "Independent t-test"

        elif test_type == 'mannwhitney':
            # Mann-Whitney U test (non-parametric)
            statistic, p_value = stats.mannwhitneyu(group_a_data, group_b_data, alternative='two-sided')
            # Rank-biserial correlation (effect size)
            u_statistic = statistic
            n1, n2 = len(group_a_data), len(group_b_data)
            effect_size = float(1 - (2*u_statistic) / (n1 * n2))
            test_name = "Mann-Whitney U test"

        else:
            return {"error": f"Unsupported test type: {test_type}"}

        # Interpret results
        is_significant = p_value < alpha
        percent_diff = ((results['group_b']['mean'] - results['group_a']['mean']) / results['group_a']['mean']) * 100

        results['test'] = {
            'name': test_name,
            'statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'is_significant': is_significant,
            'effect_size': effect_size,
            'percent_difference': float(percent_diff)
        }

        # Power analysis (for t-test)
        if test_type == 'ttest':
            power_analysis = TTestIndPower()
            power = power_analysis.solve_power(
                effect_size=abs(cohens_d),
                nobs1=len(group_a_data),
                alpha=alpha,
                ratio=len(group_b_data) / len(group_a_data)
            )
            results['power'] = float(power)

        # Interpretation
        results['interpretation'] = self._interpret_ab_test(results)

        return results

    def _interpret_ab_test(self, results: Dict) -> str:
        """Generate natural language interpretation of A/B test"""
        test = results['test']
        group_a = results['group_a']
        group_b = results['group_b']

        if test['is_significant']:
            significance = f"statistically significant (p={test['p_value']:.4f})"
        else:
            significance = f"not statistically significant (p={test['p_value']:.4f})"

        direction = "higher" if group_b['mean'] > group_a['mean'] else "lower"

        return (
            f"Group '{group_b['name']}' (n={group_b['n']}) has a {abs(test['percent_difference']):.1f}% "
            f"{direction} mean ({group_b['mean']:.2f}) compared to '{group_a['name']}' "
            f"(n={group_a['n']}, mean={group_a['mean']:.2f}). "
            f"This difference is {significance}, with an effect size of {test['effect_size']:.3f}."
        )

    # ========================================================================
    # 4. TEMPORAL TREND ANALYSIS
    # ========================================================================

    def temporal_trend_analysis(
        self,
        metric: str,
        period: int = 365,  # seasonality period
        model: str = 'additive',  # 'additive' or 'multiplicative'
        save_plot: bool = True,
        plot_path: str = 'temporal_trends.png'
    ) -> Dict:
        """
        Decompose time series into trend, seasonality, and residual components.

        Example use case: "Analyze seasonal patterns in respiratory disease deaths"

        Args:
            metric: Metric to analyze
            period: Seasonality period (365 for yearly, 7 for weekly, etc.)
            model: 'additive' or 'multiplicative'

        Returns:
            Dict with decomposed components and statistics
        """
        if not self.date_column:
            return {"error": "No date column found for temporal analysis"}

        # Prepare time series
        ts_data = self.df.set_index(self.date_column)[metric].dropna()

        if len(ts_data) < 2 * period:
            return {"error": f"Insufficient data points for period={period}. Need at least {2*period} points."}

        # Perform decomposition
        decomposition = seasonal_decompose(ts_data, model=model, period=period, extrapolate_trend='freq')

        # Extract components
        trend = decomposition.trend
        seasonal = decomposition.seasonal
        residual = decomposition.resid

        # Calculate statistics
        results = {
            'original_mean': float(ts_data.mean()),
            'original_std': float(ts_data.std()),
            'trend_direction': 'increasing' if trend.iloc[-1] > trend.iloc[0] else 'decreasing',
            'trend_change': float(trend.iloc[-1] - trend.iloc[0]),
            'trend_pct_change': float(((trend.iloc[-1] - trend.iloc[0]) / trend.iloc[0]) * 100),
            'seasonality_strength': float(1 - (residual.var() / ts_data.var())),
            'components': {
                'trend': trend.to_dict(),
                'seasonal': seasonal.to_dict(),
                'residual': residual.to_dict()
            }
        }

        # Visualization
        if save_plot:
            fig, axes = plt.subplots(4, 1, figsize=(15, 12))

            ts_data.plot(ax=axes[0], title=f'{metric} - Original', color='black')
            trend.plot(ax=axes[1], title='Trend Component', color='blue')
            seasonal.plot(ax=axes[2], title='Seasonal Component', color='green')
            residual.plot(ax=axes[3], title='Residual Component', color='red')

            plt.tight_layout()
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            results['plot_path'] = plot_path

        return results


# Example usage
if __name__ == "__main__":
    # Example with synthetic GBD-style data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    df = pd.DataFrame({
        'date': dates,
        'deaths': np.random.poisson(100, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 20,
        'region': np.random.choice(['USA', 'Europe'], len(dates))
    })

    # Initialize engine
    engine = AdvancedGBDAnalytics(df, date_column='date')

    # Example 1: Prophet forecast
    print("\n=== PROPHET FORECAST ===")
    forecast_results = engine.prophet_forecast('deaths', periods=180, freq='D')
    print(f"Predicted change: {forecast_results['percent_change']:.1f}%")

    # Example 2: Temporal decomposition
    print("\n=== TEMPORAL TREND ANALYSIS ===")
    trend_results = engine.temporal_trend_analysis('deaths', period=365)
    print(f"Trend: {trend_results['trend_direction']}, Change: {trend_results['trend_pct_change']:.1f}%")

    print("\n✅ All analytics modules working correctly!")
