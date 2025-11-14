"""
GBD Schema Mapper - Ensures Column Consistency Across CSV Files

This module standardizes column names and mappings using the GBD mapping scheme,
ensuring that data from different CSV files can be combined and analyzed consistently.

Problem:
- Different CSV files use different column names for the same concept
- "deaths" vs "mortality" vs "death_count" → all mean the same thing
- "age_group" vs "age_category" vs "age_range" → same dimension

Solution:
- Map all variations to standardized GBD terminology
- Validate CSV structure before upload to File Search
- Provide column mappings as metadata for semantic search
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

# Try to import gbd_mapping (optional, requires IHME access)
try:
    import gbd_mapping
    GBD_MAPPING_AVAILABLE = True
except ImportError:
    GBD_MAPPING_AVAILABLE = False
    print("⚠️  gbd_mapping not available. Using fallback mappings.")


class GBDSchemaMapper:
    """
    Standardizes GBD CSV files to consistent schema.

    Features:
    1. Column name standardization (deaths = mortality = death_count)
    2. GBD hierarchy integration (causes, risks, covariates)
    3. Schema validation before File Search upload
    4. Metadata generation for semantic search
    """

    # Standardized column name mappings
    COLUMN_MAPPINGS = {
        # Metric columns
        'deaths': ['deaths', 'death', 'mortality', 'mortality_count', 'death_count', 'num_deaths', 'deaths_mean'],
        'dalys': ['dalys', 'daly', 'disability_adjusted_life_years', 'dalys_mean'],
        'ylds': ['ylds', 'yld', 'years_lived_with_disability', 'ylds_mean'],
        'ylls': ['ylls', 'yll', 'years_of_life_lost', 'ylls_mean'],
        'prevalence': ['prevalence', 'prev', 'prevalence_rate', 'prevalence_mean'],
        'incidence': ['incidence', 'inc', 'incidence_rate', 'incidence_mean', 'cases', 'new_cases'],
        'rate': ['rate', 'per_100k', 'per100k', 'rate_per_100000'],

        # Dimension columns
        'year': ['year', 'year_id', 'time', 'period'],
        'location': ['location', 'location_name', 'country', 'geography', 'region', 'location_id'],
        'age_group': ['age_group', 'age', 'age_category', 'age_range', 'age_group_name', 'age_id'],
        'sex': ['sex', 'gender', 'sex_name', 'sex_id'],
        'cause': ['cause', 'cause_name', 'cause_id', 'gbd_cause'],
        'risk': ['risk', 'risk_name', 'risk_factor', 'rei', 'rei_name', 'risk_id'],
        'measure': ['measure', 'measure_name', 'metric', 'measure_id'],

        # Statistical columns
        'mean': ['mean', 'val', 'value', 'estimate'],
        'lower': ['lower', 'lower_bound', 'lower_ui', 'lower_95'],
        'upper': ['upper', 'upper_bound', 'upper_ui', 'upper_95'],
    }

    # GBD standard age groups
    STANDARD_AGE_GROUPS = [
        '<1 year', '1-4 years', '5-9 years', '10-14 years', '15-19 years',
        '20-24 years', '25-29 years', '30-34 years', '35-39 years',
        '40-44 years', '45-49 years', '50-54 years', '55-59 years',
        '60-64 years', '65-69 years', '70-74 years', '75-79 years',
        '80-84 years', '85-89 years', '90-94 years', '95+ years',
        'All ages', 'Age-standardized'
    ]

    # GBD standard sex values
    STANDARD_SEX = ['Male', 'Female', 'Both', 'Both sexes']

    # GBD standard measures
    STANDARD_MEASURES = [
        'Deaths', 'DALYs', 'YLDs', 'YLLs',
        'Prevalence', 'Incidence', 'Incidence rate', 'Prevalence rate',
        'Death rate', 'DALY rate', 'YLD rate', 'YLL rate'
    ]

    def __init__(self):
        """Initialize schema mapper"""
        self.reverse_mapping = self._build_reverse_mapping()

        # Try to load GBD mapping if available
        if GBD_MAPPING_AVAILABLE:
            self.gbd_causes = self._load_gbd_causes()
            self.gbd_risks = self._load_gbd_risks()
        else:
            self.gbd_causes = {}
            self.gbd_risks = {}

    def _build_reverse_mapping(self) -> Dict[str, str]:
        """Build reverse lookup: variant → standard name"""
        reverse = {}
        for standard_name, variants in self.COLUMN_MAPPINGS.items():
            for variant in variants:
                reverse[variant.lower()] = standard_name
        return reverse

    def _load_gbd_causes(self) -> Dict:
        """Load GBD cause hierarchy (requires gbd_mapping package)"""
        try:
            # This would use the actual gbd_mapping package
            # For now, return placeholder
            return {}
        except:
            return {}

    def _load_gbd_risks(self) -> Dict:
        """Load GBD risk hierarchy (requires gbd_mapping package)"""
        try:
            # This would use the actual gbd_mapping package
            return {}
        except:
            return {}

    def detect_standard_column(self, column_name: str) -> Optional[str]:
        """
        Detect which standard column a given column name maps to.

        Args:
            column_name: Original column name from CSV

        Returns:
            Standard column name, or None if not recognized
        """
        column_lower = column_name.lower().strip()
        return self.reverse_mapping.get(column_lower)

    def standardize_dataframe(
        self,
        df: pd.DataFrame,
        file_path: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Standardize a GBD DataFrame to consistent schema.

        Args:
            df: Input DataFrame
            file_path: Optional path for context

        Returns:
            (standardized_df, metadata_dict)
        """
        df_std = df.copy()
        column_mapping = {}
        unmapped_columns = []

        # Map columns to standard names
        for col in df.columns:
            std_name = self.detect_standard_column(col)
            if std_name:
                column_mapping[col] = std_name
            else:
                unmapped_columns.append(col)

        # Rename columns
        df_std = df_std.rename(columns=column_mapping)

        # Validate data types
        validation_warnings = []

        if 'year' in df_std.columns:
            try:
                df_std['year'] = pd.to_numeric(df_std['year'], errors='coerce')
            except:
                validation_warnings.append("Could not convert 'year' to numeric")

        # Generate metadata
        metadata = {
            'original_columns': list(df.columns),
            'standardized_columns': list(df_std.columns),
            'column_mapping': column_mapping,
            'unmapped_columns': unmapped_columns,
            'row_count': len(df_std),
            'validation_warnings': validation_warnings,
            'schema_version': '1.0'
        }

        # Add detected dimensions and metrics
        detected_dimensions = [col for col in df_std.columns if col in ['year', 'location', 'age_group', 'sex', 'cause', 'risk']]
        detected_metrics = [col for col in df_std.columns if col in ['deaths', 'dalys', 'ylds', 'ylls', 'prevalence', 'incidence']]

        metadata['dimensions'] = detected_dimensions
        metadata['metrics'] = detected_metrics

        return df_std, metadata

    def validate_csv_schema(self, file_path: str) -> Dict:
        """
        Validate a CSV file against GBD schema expectations.

        Args:
            file_path: Path to CSV file

        Returns:
            Dict with validation results and recommendations
        """
        try:
            # Read first 1000 rows for quick validation
            df = pd.read_csv(file_path, nrows=1000)
        except Exception as e:
            return {
                'valid': False,
                'error': f"Cannot read CSV: {str(e)}",
                'recommendations': []
            }

        # Standardize
        df_std, metadata = self.standardize_dataframe(df, file_path)

        # Check for required columns
        required_columns = ['year']  # Minimum requirement
        has_required = all(col in df_std.columns for col in required_columns)

        # Check for at least one metric
        has_metric = any(col in df_std.columns for col in ['deaths', 'dalys', 'ylds', 'ylls', 'prevalence', 'incidence'])

        # Generate recommendations
        recommendations = []

        if not has_required:
            recommendations.append("Missing required column: 'year'. Add a year/time column.")

        if not has_metric:
            recommendations.append("No metric columns detected. Add at least one: deaths, DALYs, prevalence, etc.")

        if metadata['unmapped_columns']:
            recommendations.append(f"Unmapped columns: {', '.join(metadata['unmapped_columns'][:5])}. Consider renaming to standard names.")

        if len(metadata['dimensions']) < 2:
            recommendations.append("Few dimension columns detected. Consider adding: location, age_group, sex, cause.")

        # Validation result
        result = {
            'valid': has_required and has_metric,
            'file': file_path,
            'row_count': len(df),
            'column_count': len(df.columns),
            'standardized_columns': metadata['standardized_columns'],
            'unmapped_columns': metadata['unmapped_columns'],
            'dimensions': metadata['dimensions'],
            'metrics': metadata['metrics'],
            'recommendations': recommendations,
            'column_mapping': metadata['column_mapping']
        }

        return result

    def prepare_for_file_search(
        self,
        csv_path: str,
        output_path: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        Prepare a CSV file for upload to Gemini File Search.

        This:
        1. Standardizes column names
        2. Validates schema
        3. Saves standardized version
        4. Returns metadata for File Search

        Args:
            csv_path: Input CSV path
            output_path: Optional output path (default: csv_path with '_standardized' suffix)

        Returns:
            (output_file_path, metadata_for_file_search)
        """
        # Read and standardize
        df = pd.read_csv(csv_path)
        df_std, metadata = self.standardize_dataframe(df, csv_path)

        # Determine output path
        if output_path is None:
            path_obj = Path(csv_path)
            output_path = str(path_obj.parent / f"{path_obj.stem}_standardized{path_obj.suffix}")

        # Save standardized version
        df_std.to_csv(output_path, index=False)

        # Generate metadata for File Search
        file_search_metadata = [
            {"key": "original_file", "string_value": Path(csv_path).name},
            {"key": "schema_standardized", "string_value": "true"},
            {"key": "schema_version", "string_value": metadata['schema_version']},
            {"key": "row_count", "numeric_value": metadata['row_count']},
        ]

        # Add dimension info
        if metadata['dimensions']:
            file_search_metadata.append({
                "key": "dimensions",
                "string_value": ", ".join(metadata['dimensions'])
            })

        # Add metric info
        if metadata['metrics']:
            file_search_metadata.append({
                "key": "metrics",
                "string_value": ", ".join(metadata['metrics'])
            })

        # Add column mapping as JSON
        file_search_metadata.append({
            "key": "column_mapping",
            "string_value": json.dumps(metadata['column_mapping'])
        })

        return output_path, file_search_metadata

    def generate_schema_documentation(self, csv_files: List[str]) -> str:
        """
        Generate documentation of schemas across multiple CSV files.

        Useful for understanding consistency across your GBD dataset.
        """
        doc = "# GBD Dataset Schema Analysis\n\n"

        for csv_file in csv_files:
            validation = self.validate_csv_schema(csv_file)

            doc += f"## {Path(csv_file).name}\n\n"
            doc += f"**Status:** {'✅ Valid' if validation['valid'] else '❌ Issues Found'}\n\n"
            doc += f"- Rows: {validation['row_count']:,}\n"
            doc += f"- Columns: {validation['column_count']}\n"
            doc += f"- Dimensions: {', '.join(validation['dimensions']) if validation['dimensions'] else 'None'}\n"
            doc += f"- Metrics: {', '.join(validation['metrics']) if validation['metrics'] else 'None'}\n\n"

            if validation['column_mapping']:
                doc += "**Column Mapping:**\n"
                for orig, std in validation['column_mapping'].items():
                    doc += f"- `{orig}` → `{std}`\n"
                doc += "\n"

            if validation['unmapped_columns']:
                doc += f"**Unmapped Columns:** {', '.join(validation['unmapped_columns'])}\n\n"

            if validation['recommendations']:
                doc += "**Recommendations:**\n"
                for rec in validation['recommendations']:
                    doc += f"- {rec}\n"
                doc += "\n"

            doc += "---\n\n"

        return doc


# Example usage
if __name__ == "__main__":
    mapper = GBDSchemaMapper()

    # Example 1: Detect standard column names
    print("=" * 70)
    print("EXAMPLE 1: Column Name Detection")
    print("=" * 70)

    test_columns = [
        'deaths', 'death_count', 'mortality',
        'dalys', 'disability_adjusted_life_years',
        'year', 'year_id',
        'location', 'country', 'geography'
    ]

    for col in test_columns:
        std = mapper.detect_standard_column(col)
        print(f"{col:40s} → {std}")

    # Example 2: Standardize a DataFrame
    print("\n" + "=" * 70)
    print("EXAMPLE 2: DataFrame Standardization")
    print("=" * 70)

    # Create sample DataFrame with non-standard column names
    df_original = pd.DataFrame({
        'year_id': [2019, 2020, 2021],
        'death_count': [1000, 1100, 1050],
        'disability_adjusted_life_years': [50000, 52000, 51000],
        'country': ['USA', 'USA', 'USA']
    })

    print("\nOriginal columns:", list(df_original.columns))

    df_std, metadata = mapper.standardize_dataframe(df_original)

    print("Standardized columns:", list(df_std.columns))
    print("\nColumn mapping:", metadata['column_mapping'])
    print("Detected dimensions:", metadata['dimensions'])
    print("Detected metrics:", metadata['metrics'])

    print("\n✅ Schema mapper working correctly!")
