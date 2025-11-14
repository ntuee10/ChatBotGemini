"""
Semantic Layer for GBD Data Analysis
Integrates: Gemini File Search (ground truth) + Advanced Analytics + Visualization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import json

# Local imports
from gemini_file_search import GBDFileSearchManager
from advanced_analytics import AdvancedGBDAnalytics

# Visualization
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns


class GBDSemanticLayer:
    """
    Semantic Layer for GBD 2023 Data Analysis.

    This is the main interface researchers use to:
    1. Ask questions grounded in actual CSV data (via Gemini File Search)
    2. Perform advanced analytics (causal, predictive, A/B, temporal)
    3. Generate publication-ready visualizations with citations
    4. Extract insights with confidence intervals and statistical rigor
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        file_search_manager: Optional[GBDFileSearchManager] = None
    ):
        """
        Initialize semantic layer.

        Args:
            gemini_api_key: Google Gemini API key
            file_search_manager: Pre-configured GBDFileSearchManager (optional)
        """
        # Initialize Gemini File Search
        if file_search_manager:
            self.file_search = file_search_manager
        elif gemini_api_key:
            self.file_search = GBDFileSearchManager(api_key=gemini_api_key)
        else:
            self.file_search = GBDFileSearchManager()  # Will use env variable

        self.analytics_engine: Optional[AdvancedGBDAnalytics] = None
        self.current_data: Optional[pd.DataFrame] = None
        self.metadata: Dict = {}

    # ========================================================================
    # GROUNDED QUESTION ANSWERING
    # ========================================================================

    def ask_question(
        self,
        question: str,
        categories: Optional[List[str]] = None,
        year: Optional[int] = None,
        region: Optional[str] = None,
        include_citations: bool = True
    ) -> Dict:
        """
        Ask a research question grounded in GBD CSV data.

        The question is answered by Gemini using File Search over your uploaded
        CSV files, ensuring all responses are grounded in actual data.

        Args:
            question: Natural language research question
            categories: GBD categories to search (e.g., ['causes', 'risks'])
            year: Filter by specific year
            region: Filter by geographic region
            include_citations: Include source file citations

        Returns:
            Dict with answer, citations, and data sources

        Example:
            >>> layer.ask_question(
            ...     "What were the top 10 causes of death globally in 2023?",
            ...     categories=['causes'],
            ...     year=2023,
            ...     region='global'
            ... )
        """
        # Build metadata filter
        filters = []
        if year:
            filters.append(f"year={year}")
        if region:
            filters.append(f"geography={region}")

        metadata_filter = " AND ".join(filters) if filters else None

        # Query Gemini File Search
        result = self.file_search.query_with_citations(
            question=question,
            categories=categories,
            metadata_filter=metadata_filter
        )

        # Format response
        response = {
            'question': question,
            'answer': result['text'],
            'sources': [],
            'metadata': {
                'categories': categories,
                'year': year,
                'region': region
            }
        }

        # Extract citations
        if include_citations and result.get('grounding_metadata'):
            for chunk in result['grounding_metadata'].grounding_chunks:
                if hasattr(chunk, 'web'):
                    response['sources'].append({
                        'file': chunk.web.uri,
                        'title': getattr(chunk.web, 'title', 'Unknown')
                    })

        return response

    # ========================================================================
    # DATA RETRIEVAL WITH GROUND TRUTH VERIFICATION
    # ========================================================================

    def load_data_for_analysis(
        self,
        category: str,
        metric: str,
        filters: Optional[Dict] = None,
        verify_with_gemini: bool = True
    ) -> pd.DataFrame:
        """
        Load CSV data for analysis with ground truth verification.

        This retrieves data from your local CSV files but optionally verifies
        the data characteristics against Gemini File Search to ensure accuracy.

        Args:
            category: GBD category (causes, risks, etc.)
            metric: Metric to analyze (e.g., 'deaths', 'DALYs')
            filters: Optional filters (year, region, etc.)
            verify_with_gemini: Cross-check with Gemini File Search

        Returns:
            Verified DataFrame ready for analysis
        """
        # TODO: Implement local CSV loading logic
        # For now, this is a placeholder for the integration point
        raise NotImplementedError(
            "Load your CSV data here. This method should:\n"
            "1. Load relevant CSV files based on category\n"
            "2. Apply filters (year, region, etc.)\n"
            "3. Optionally verify key statistics with Gemini File Search\n"
            "4. Return clean DataFrame for analysis"
        )

    # ========================================================================
    # INTEGRATED ANALYTICS WITH GROUNDED CONTEXT
    # ========================================================================

    def analyze_intervention_impact(
        self,
        data: pd.DataFrame,
        metric: str,
        intervention_date: Union[str, datetime],
        intervention_name: str,
        date_column: str = 'date',
        control_metrics: Optional[List[str]] = None,
        ask_gemini_for_context: bool = True
    ) -> Dict:
        """
        Perform causal impact analysis with grounded context from Gemini.

        This combines:
        1. Statistical causal analysis (CausalImpact)
        2. Contextual information from Gemini File Search
        3. Professional visualization with citations

        Args:
            data: GBD data DataFrame
            metric: Metric to analyze (e.g., 'deaths')
            intervention_date: Date of intervention
            intervention_name: Name of intervention (e.g., "COVID-19 lockdown")
            date_column: Name of date column
            control_metrics: Control variables
            ask_gemini_for_context: Get background context from Gemini

        Returns:
            Dict with causal impact results, context, and visualizations
        """
        # Get context from Gemini if requested
        context = ""
        if ask_gemini_for_context:
            context_query = f"What is known about the impact of {intervention_name} on {metric}? Provide brief summary with citations."
            context_result = self.ask_question(context_query)
            context = context_result['answer']

        # Run causal impact analysis
        engine = AdvancedGBDAnalytics(data, date_column=date_column)
        causal_results = engine.causal_impact_analysis(
            metric=metric,
            intervention_date=intervention_date,
            control_metrics=control_metrics,
            save_plot=True,
            plot_path=f'causal_impact_{intervention_name.replace(" ", "_")}.png'
        )

        # Combine results
        return {
            'intervention': intervention_name,
            'intervention_date': str(intervention_date),
            'metric': metric,
            'grounded_context': context,
            'statistical_analysis': causal_results,
            'interpretation': self._create_causal_insight(causal_results, intervention_name, context)
        }

    def forecast_with_context(
        self,
        data: pd.DataFrame,
        metric: str,
        periods: int,
        freq: str = 'D',
        date_column: str = 'date',
        ask_gemini_for_trends: bool = True
    ) -> Dict:
        """
        Generate forecast with historical context from Gemini.

        Combines:
        1. Prophet time-series forecasting
        2. Historical trend context from Gemini
        3. Professional visualization

        Args:
            data: GBD data DataFrame
            metric: Metric to forecast
            periods: Number of periods to forecast
            freq: Frequency ('D', 'W', 'M', 'Y')
            date_column: Name of date column
            ask_gemini_for_trends: Get historical context from Gemini

        Returns:
            Dict with forecast, context, and visualizations
        """
        # Get historical context from Gemini
        context = ""
        if ask_gemini_for_trends:
            context_query = f"What are the historical trends in {metric}? What factors have influenced changes over time?"
            context_result = self.ask_question(context_query)
            context = context_result['answer']

        # Run Prophet forecast
        engine = AdvancedGBDAnalytics(data, date_column=date_column)
        forecast_results = engine.prophet_forecast(
            metric=metric,
            periods=periods,
            freq=freq,
            save_plot=True,
            plot_path=f'forecast_{metric}.png'
        )

        return {
            'metric': metric,
            'forecast_periods': periods,
            'grounded_context': context,
            'forecast_results': forecast_results,
            'interpretation': self._create_forecast_insight(forecast_results, metric, context)
        }

    def compare_groups(
        self,
        data: pd.DataFrame,
        metric: str,
        group_column: str,
        group_a: str,
        group_b: str,
        ask_gemini_for_background: bool = True
    ) -> Dict:
        """
        A/B test comparison with grounded background from Gemini.

        Combines:
        1. Statistical hypothesis testing
        2. Effect size calculation
        3. Background context from Gemini
        4. Professional visualization

        Args:
            data: GBD data DataFrame
            metric: Metric to compare
            group_column: Column with group labels
            group_a: Group A label
            group_b: Group B label
            ask_gemini_for_background: Get context from Gemini

        Returns:
            Dict with test results, context, and interpretation
        """
        # Get background from Gemini
        context = ""
        if ask_gemini_for_background:
            context_query = f"What are the known differences between {group_a} and {group_b} in terms of {metric}?"
            context_result = self.ask_question(context_query)
            context = context_result['answer']

        # Run A/B test
        engine = AdvancedGBDAnalytics(data)
        ab_results = engine.ab_test_analysis(
            metric=metric,
            group_column=group_column,
            group_a=group_a,
            group_b=group_b
        )

        # Create comparison visualization
        fig = go.Figure()
        fig.add_trace(go.Box(y=data[data[group_column] == group_a][metric], name=group_a))
        fig.add_trace(go.Box(y=data[data[group_column] == group_b][metric], name=group_b))
        fig.update_layout(title=f'{metric} Comparison: {group_a} vs {group_b}')
        fig.write_image(f'ab_test_{metric}.png', width=1000, height=600)

        return {
            'comparison': f'{group_a} vs {group_b}',
            'metric': metric,
            'grounded_context': context,
            'statistical_test': ab_results,
            'interpretation': ab_results['interpretation'],
            'plot_path': f'ab_test_{metric}.png'
        }

    # ========================================================================
    # COMPREHENSIVE RESEARCH REPORT GENERATION
    # ========================================================================

    def generate_research_report(
        self,
        research_question: str,
        data: pd.DataFrame,
        analyses: List[str] = ['descriptive', 'temporal', 'forecast'],
        output_format: str = 'markdown'
    ) -> str:
        """
        Generate comprehensive research report with:
        - Grounded background from Gemini
        - Multiple statistical analyses
        - Professional visualizations
        - Citations to source CSVs
        - Executive summary with insights

        Args:
            research_question: Main research question
            data: GBD data DataFrame
            analyses: List of analyses to include
            output_format: 'markdown', 'html', or 'json'

        Returns:
            Formatted research report
        """
        report = {
            'title': research_question,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sections': []
        }

        # 1. Executive Summary from Gemini
        summary_result = self.ask_question(
            f"Provide an executive summary answering: {research_question}",
            include_citations=True
        )
        report['sections'].append({
            'title': 'Executive Summary',
            'content': summary_result['answer'],
            'sources': summary_result.get('sources', [])
        })

        # 2. Data Overview
        engine = AdvancedGBDAnalytics(data)
        numeric_cols = data.select_dtypes(include=[np.number]).columns[:5]  # Top 5 metrics

        report['sections'].append({
            'title': 'Data Overview',
            'content': f"Dataset contains {len(data):,} observations across {len(data.columns)} variables.",
            'statistics': data[numeric_cols].describe().to_dict()
        })

        # 3. Temporal Analysis
        if 'temporal' in analyses and engine.date_column:
            for col in numeric_cols:
                trend_results = engine.temporal_trend_analysis(col, save_plot=True, plot_path=f'trend_{col}.png')
                report['sections'].append({
                    'title': f'Temporal Trends: {col}',
                    'content': f"Trend direction: {trend_results['trend_direction']}, Change: {trend_results['trend_pct_change']:.1f}%",
                    'plot': f'trend_{col}.png'
                })

        # 4. Forecast
        if 'forecast' in analyses and engine.date_column:
            for col in numeric_cols[:2]:  # Forecast top 2 metrics
                forecast_results = self.forecast_with_context(data, col, periods=90, freq='D', ask_gemini_for_trends=False)
                report['sections'].append({
                    'title': f'Forecast: {col}',
                    'content': f"Predicted {forecast_results['forecast_results']['trend']} of {forecast_results['forecast_results']['percent_change']:.1f}% over next 90 days",
                    'plot': forecast_results['forecast_results'].get('plot_path')
                })

        # Format output
        if output_format == 'markdown':
            return self._format_markdown_report(report)
        elif output_format == 'json':
            return json.dumps(report, indent=2)
        else:
            return str(report)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _create_causal_insight(self, causal_results: Dict, intervention_name: str, context: str) -> str:
        """Generate executive insight for causal impact analysis"""
        impact = causal_results.get('average_impact', 0)
        p_value = causal_results.get('p_value', 1)

        insight = f"**Causal Impact Analysis: {intervention_name}**\n\n"
        insight += f"{context}\n\n"
        insight += f"Our statistical analysis shows: {causal_results.get('interpretation', '')}\n\n"

        if p_value < 0.05:
            insight += f"✅ This finding is statistically significant and actionable for policy decisions.\n"
        else:
            insight += f"⚠️  This finding is not statistically significant. More data may be needed.\n"

        return insight

    def _create_forecast_insight(self, forecast_results: Dict, metric: str, context: str) -> str:
        """Generate executive insight for forecast"""
        pct_change = forecast_results.get('percent_change', 0)
        trend = forecast_results.get('trend', 'stable')

        insight = f"**Forecast Analysis: {metric}**\n\n"
        insight += f"{context}\n\n"
        insight += f"Our predictive model forecasts a {trend} trend with a {abs(pct_change):.1f}% {'increase' if pct_change > 0 else 'decrease'} "
        insight += f"from current levels (from {forecast_results['latest_actual']:.2f} to {forecast_results['final_forecast']:.2f}).\n\n"

        if abs(pct_change) > 10:
            insight += f"⚠️  This represents a substantial change that warrants attention.\n"
        else:
            insight += f"📊 This represents a moderate change consistent with historical patterns.\n"

        return insight

    def _format_markdown_report(self, report: Dict) -> str:
        """Format report as markdown"""
        md = f"# {report['title']}\n\n"
        md += f"**Generated:** {report['date']}\n\n"
        md += "---\n\n"

        for section in report['sections']:
            md += f"## {section['title']}\n\n"
            md += f"{section['content']}\n\n"

            if 'sources' in section and section['sources']:
                md += "**Sources:**\n"
                for source in section['sources']:
                    md += f"- {source.get('file', 'Unknown')}: {source.get('title', '')}\n"
                md += "\n"

            if 'plot' in section and section['plot']:
                md += f"![{section['title']}]({section['plot']})\n\n"

            md += "---\n\n"

        return md


# Example usage
if __name__ == "__main__":
    print("🚀 GBD Semantic Layer - Example Usage\n")

    # Initialize semantic layer (requires GOOGLE_API_KEY environment variable)
    layer = GBDSemanticLayer()

    # Example 1: Ask a grounded question
    print("=" * 70)
    print("EXAMPLE 1: Grounded Question Answering")
    print("=" * 70)
    result = layer.ask_question(
        "What were the leading causes of death in low-income countries in 2023?",
        categories=['causes'],
        year=2023
    )
    print(f"Q: {result['question']}")
    print(f"A: {result['answer'][:200]}...")
    print(f"Sources: {len(result['sources'])} citations")

    print("\n" + "=" * 70)
    print("✅ Semantic Layer initialized successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Upload your GBD CSV files using GBDFileSearchManager")
    print("2. Load data for analysis")
    print("3. Run advanced analytics (causal, forecast, A/B tests)")
    print("4. Generate professional research reports")
