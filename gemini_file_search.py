"""
Gemini File Search Integration for GBD CSV Data
Handles batch upload, metadata tagging, and semantic search
"""

from google import genai
from google.genai import types
import time
import os
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class GBDFileSearchManager:
    """
    Manages Gemini File Search stores for GBD 2023 dataset.

    Features:
    - Creates organized file search stores (causes, risks, covariates, etc.)
    - Batch uploads CSV files with metadata tagging
    - Handles files >100MB by splitting
    - Provides semantic search with citation support
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        if api_key:
            os.environ['GOOGLE_API_KEY'] = api_key
        self.client = genai.Client()
        self.stores: Dict[str, str] = {}  # category -> store_name mapping

    def create_gbd_stores(self):
        """
        Create organized File Search stores for GBD data categories.
        Keeps each store under 20GB for optimal performance.
        """
        categories = [
            'causes',
            'risks',
            'covariates',
            'etiologies',
            'sequelae',
            'general'  # For mixed or uncategorized data
        ]

        print("Creating GBD File Search stores...")
        for category in categories:
            store = self.client.file_search_stores.create(
                config={'display_name': f'gbd-2023-{category}'}
            )
            self.stores[category] = store.name
            print(f"✓ Created store: {category} ({store.name})")

        return self.stores

    def split_large_csv(self, file_path: str, max_size_mb: int = 95) -> List[str]:
        """
        Split CSV files larger than 100MB into smaller chunks.
        Returns list of file paths (original if small enough, or split files).
        """
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if file_size_mb <= max_size_mb:
            return [file_path]

        print(f"⚠️  File {file_path} is {file_size_mb:.1f}MB, splitting...")

        # Calculate rows per chunk to stay under max_size_mb
        df = pd.read_csv(file_path, nrows=10000)  # Sample for estimation
        rows_sample = len(df)
        size_sample_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        rows_per_chunk = int((max_size_mb / size_sample_mb) * rows_sample * 0.9)  # 90% safety margin

        # Split file
        split_files = []
        base_name = Path(file_path).stem
        base_dir = Path(file_path).parent

        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=rows_per_chunk)):
            chunk_file = base_dir / f"{base_name}_part{i+1}.csv"
            chunk.to_csv(chunk_file, index=False)
            split_files.append(str(chunk_file))
            print(f"  ✓ Created chunk {i+1}: {chunk_file}")

        return split_files

    def extract_metadata_from_filename(self, file_path: str) -> Dict[str, any]:
        """
        Extract comprehensive metadata from GBD file naming conventions.

        Example filenames:
        - "IHME_GBD_2023_CAUSES_MORTALITY_AGE_STANDARDIZED_GLOBAL_2023.csv"
        - "IHME_GBD_2021_RISKS_DALYS_BOTH_SEXES_USA_2021.csv"
        - "GBD_2023_COVARIATES_PREVALENCE_DIABETES_NATIONAL_INDIA.csv"

        Extracted metadata:
        - organization: IHME, GBD
        - dataset: GBD
        - year: 2023, 2021
        - category: causes, risks, covariates, etiologies, sequelae
        - metric: mortality, dalys, prevalence, incidence, ylds, ylls
        - age_adjustment: age_standardized, crude, age_specific
        - sex: both_sexes, male, female, both
        - geography: global, national, regional, country codes (USA, IND, etc.)
        - disease/condition: diabetes, cardiovascular, respiratory, etc.
        - measure: deaths, rate, count, percent
        """
        filename = Path(file_path).stem
        filepath_name = Path(file_path).name
        metadata = []

        # Add full filename as searchable metadata
        metadata.append({"key": "filename", "string_value": filepath_name})
        metadata.append({"key": "file_stem", "string_value": filename})

        # Parse filename parts
        parts = filename.upper().split('_')
        parts_lower = filename.lower().split('_')

        # 1. Organization (IHME, WHO, etc.)
        if 'IHME' in parts:
            metadata.append({"key": "organization", "string_value": "IHME"})
        elif 'WHO' in parts:
            metadata.append({"key": "organization", "string_value": "WHO"})

        # 2. Dataset identifier
        if 'GBD' in parts:
            metadata.append({"key": "dataset", "string_value": "GBD"})

        # 3. Year - multiple detection strategies
        for i, part in enumerate(parts):
            # Detect 4-digit year (2019, 2020, 2021, 2023, etc.)
            if part.isdigit() and len(part) == 4 and part.startswith('20'):
                metadata.append({"key": "year", "numeric_value": int(part)})
                metadata.append({"key": "year_str", "string_value": part})

            # Detect Y2023 format
            if part.startswith('Y') and part[1:].isdigit() and len(part) == 5:
                metadata.append({"key": "year", "numeric_value": int(part[1:])})
                metadata.append({"key": "year_str", "string_value": part[1:]})

        # 4. Category (causes, risks, etc.)
        gbd_categories = {
            'causes': 'causes',
            'cause': 'causes',
            'risks': 'risks',
            'risk': 'risks',
            'covariates': 'covariates',
            'covariate': 'covariates',
            'etiologies': 'etiologies',
            'etiology': 'etiologies',
            'sequelae': 'sequelae',
            'sequela': 'sequelae',
            'rei': 'risks',  # Risk-etiology-impairment
            'impairments': 'impairments'
        }

        for part_lower in parts_lower:
            if part_lower in gbd_categories:
                metadata.append({"key": "category", "string_value": gbd_categories[part_lower]})
                metadata.append({"key": "gbd_category", "string_value": gbd_categories[part_lower]})
                break

        # 5. Metric type
        gbd_metrics = {
            'mortality': 'deaths',
            'deaths': 'deaths',
            'death': 'deaths',
            'dalys': 'dalys',
            'daly': 'dalys',
            'ylds': 'ylds',  # Years Lived with Disability
            'yld': 'ylds',
            'ylls': 'ylls',  # Years of Life Lost
            'yll': 'ylls',
            'prevalence': 'prevalence',
            'incidence': 'incidence',
            'cases': 'incidence',
            'rate': 'rate',
            'count': 'count',
            'percent': 'percent',
            'proportion': 'proportion'
        }

        for part_lower in parts_lower:
            if part_lower in gbd_metrics:
                metadata.append({"key": "metric", "string_value": gbd_metrics[part_lower]})
                metadata.append({"key": "measure", "string_value": part_lower})

        # 6. Age adjustment
        age_adjustments = ['age_standardized', 'age_specific', 'crude', 'agestandardized', 'agespecific']
        for part_lower in parts_lower:
            if part_lower in age_adjustments:
                adj_type = part_lower.replace('_', ' ').title()
                metadata.append({"key": "age_adjustment", "string_value": adj_type})

        # 7. Sex/Gender
        sex_indicators = {
            'both_sexes': 'both',
            'bothsexes': 'both',
            'both': 'both',
            'male': 'male',
            'female': 'female',
            'males': 'male',
            'females': 'female'
        }

        for part_lower in parts_lower:
            if part_lower in sex_indicators:
                metadata.append({"key": "sex", "string_value": sex_indicators[part_lower]})
                break

        # 8. Geography
        geography_levels = {
            'global': 'global',
            'world': 'global',
            'regional': 'regional',
            'region': 'regional',
            'national': 'national',
            'country': 'national',
            'subnational': 'subnational',
            'state': 'subnational',
            'province': 'subnational'
        }

        for part_lower in parts_lower:
            if part_lower in geography_levels:
                metadata.append({"key": "geography_level", "string_value": geography_levels[part_lower]})

        # Country codes (ISO 3-letter codes or common names)
        country_codes = {
            'usa': 'United States',
            'gbr': 'United Kingdom',
            'ind': 'India',
            'chn': 'China',
            'bra': 'Brazil',
            'can': 'Canada',
            'aus': 'Australia',
            'deu': 'Germany',
            'fra': 'France',
            'jpn': 'Japan',
            'mex': 'Mexico',
            'nga': 'Nigeria',
            'zaf': 'South Africa',
            'eth': 'Ethiopia',
            'egy': 'Egypt',
            'ita': 'Italy',
            'esp': 'Spain',
            'kor': 'South Korea',
            'idn': 'Indonesia',
            'pak': 'Pakistan',
            'bgd': 'Bangladesh',
            # Add more as needed
        }

        for part_lower in parts_lower:
            if part_lower in country_codes:
                metadata.append({"key": "country", "string_value": country_codes[part_lower]})
                metadata.append({"key": "country_code", "string_value": part_lower.upper()})
                metadata.append({"key": "geography_level", "string_value": "national"})

        # 9. Disease/Condition/Cause names
        # Extract potential disease names (common GBD terms)
        disease_keywords = {
            'diabetes': 'Diabetes mellitus',
            'cardiovascular': 'Cardiovascular diseases',
            'cvd': 'Cardiovascular diseases',
            'respiratory': 'Respiratory diseases',
            'copd': 'Chronic obstructive pulmonary disease',
            'cancer': 'Neoplasms',
            'neoplasms': 'Neoplasms',
            'malaria': 'Malaria',
            'hiv': 'HIV/AIDS',
            'aids': 'HIV/AIDS',
            'tuberculosis': 'Tuberculosis',
            'tb': 'Tuberculosis',
            'maternal': 'Maternal disorders',
            'neonatal': 'Neonatal disorders',
            'injuries': 'Injuries',
            'violence': 'Interpersonal violence',
            'suicide': 'Self-harm',
            'stroke': 'Stroke',
            'ihd': 'Ischemic heart disease',
            'ischemic': 'Ischemic heart disease',
            'alzheimer': 'Alzheimer disease',
            'dementia': 'Dementia',
            'depression': 'Depressive disorders',
            'anxiety': 'Anxiety disorders',
            'schizophrenia': 'Schizophrenia',
            'asthma': 'Asthma',
            'smoking': 'Smoking',
            'tobacco': 'Tobacco',
            'alcohol': 'Alcohol use',
            'drugs': 'Drug use',
            'obesity': 'High body-mass index',
            'bmi': 'High body-mass index',
            'nutrition': 'Malnutrition',
            'malnutrition': 'Malnutrition',
        }

        found_diseases = []
        for part_lower in parts_lower:
            if part_lower in disease_keywords:
                disease_name = disease_keywords[part_lower]
                found_diseases.append(disease_name)
                metadata.append({"key": "condition", "string_value": disease_name})
                metadata.append({"key": "condition_keyword", "string_value": part_lower})

        # 10. Income level (for country groups)
        income_levels = {
            'high_income': 'High income',
            'highincome': 'High income',
            'upper_middle': 'Upper middle income',
            'uppermiddle': 'Upper middle income',
            'lower_middle': 'Lower middle income',
            'lowermiddle': 'Lower middle income',
            'low_income': 'Low income',
            'lowincome': 'Low income'
        }

        for part_lower in parts_lower:
            if part_lower in income_levels:
                metadata.append({"key": "income_level", "string_value": income_levels[part_lower]})

        # 11. Age groups (if specified)
        age_groups = {
            'under5': 'Under 5 years',
            'u5': 'Under 5 years',
            'neonatal': 'Neonatal (0-27 days)',
            'infant': 'Infant (0-1 year)',
            'child': 'Child (1-14 years)',
            'adolescent': 'Adolescent (10-19 years)',
            'adult': 'Adult (20+ years)',
            'elderly': 'Elderly (65+ years)',
            'allages': 'All ages',
            'all_ages': 'All ages'
        }

        for part_lower in parts_lower:
            if part_lower in age_groups:
                metadata.append({"key": "age_group", "string_value": age_groups[part_lower]})

        # 12. Create a searchable description from filename
        # This helps Gemini understand what the file contains
        description_parts = []

        # Extract readable parts for description
        for meta in metadata:
            if meta['key'] in ['category', 'metric', 'geography_level', 'year', 'condition', 'country']:
                if 'string_value' in meta:
                    description_parts.append(meta['string_value'])
                elif 'numeric_value' in meta:
                    description_parts.append(str(meta['numeric_value']))

        if description_parts:
            description = " - ".join(description_parts[:5])  # Top 5 most relevant
            metadata.append({"key": "file_description", "string_value": description})

        # 13. Add semantic tags for better searchability
        tags = []
        if any(m['key'] == 'category' and 'causes' in m.get('string_value', '') for m in metadata):
            tags.append("mortality")
            tags.append("disease burden")

        if any(m['key'] == 'category' and 'risks' in m.get('string_value', '') for m in metadata):
            tags.append("risk factors")
            tags.append("attributable burden")

        if any(m['key'] == 'metric' and m.get('string_value') in ['dalys', 'ylds', 'ylls'] for m in metadata):
            tags.append("disability")
            tags.append("burden of disease")

        if tags:
            metadata.append({"key": "tags", "string_value": ", ".join(tags)})

        return metadata

    def upload_csv_batch(
        self,
        file_paths: List[str],
        category: str = 'general',
        custom_metadata: Optional[List[Dict]] = None
    ):
        """
        Upload multiple CSV files to a specific GBD store.

        Args:
            file_paths: List of CSV file paths
            category: GBD category (causes, risks, covariates, etc.)
            custom_metadata: Optional additional metadata for all files
        """
        if category not in self.stores:
            raise ValueError(f"Store '{category}' not found. Create stores first with create_gbd_stores()")

        store_name = self.stores[category]
        uploaded_count = 0

        print(f"\n📤 Uploading {len(file_paths)} files to '{category}' store...")

        for file_path in file_paths:
            # Split if needed
            file_chunks = self.split_large_csv(file_path)

            for chunk_file in file_chunks:
                # Extract metadata from filename
                metadata = self.extract_metadata_from_filename(chunk_file)

                # Add custom metadata if provided
                if custom_metadata:
                    metadata.extend(custom_metadata)

                # Upload and import
                display_name = Path(chunk_file).stem

                try:
                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=chunk_file,
                        file_search_store_name=store_name,
                        config={
                            'display_name': display_name,
                            'custom_metadata': metadata,
                            'chunking_config': {
                                'white_space_config': {
                                    'max_tokens_per_chunk': 500,  # Optimized for CSV data
                                    'max_overlap_tokens': 50
                                }
                            }
                        }
                    )

                    # Wait for import to complete
                    while not operation.done:
                        time.sleep(3)
                        operation = self.client.operations.get(operation)

                    print(f"  ✓ Uploaded: {display_name}")
                    uploaded_count += 1

                except Exception as e:
                    print(f"  ✗ Failed to upload {chunk_file}: {str(e)}")

        print(f"\n✅ Successfully uploaded {uploaded_count} files to '{category}' store")
        return uploaded_count

    def query_with_citations(
        self,
        question: str,
        categories: Optional[List[str]] = None,
        metadata_filter: Optional[str] = None,
        model: str = "gemini-2.5-flash"
    ) -> Dict:
        """
        Query GBD data with semantic search and get cited responses.

        Args:
            question: Natural language query
            categories: List of GBD categories to search (default: all)
            metadata_filter: Optional filter (e.g., "year=2023 AND geography=global")
            model: Gemini model to use

        Returns:
            Dict with 'text', 'citations', and 'grounding_metadata'
        """
        # Default to all stores if none specified
        if categories is None:
            categories = list(self.stores.keys())

        # Get store names for specified categories
        store_names = [self.stores[cat] for cat in categories if cat in self.stores]

        if not store_names:
            raise ValueError("No valid stores found for specified categories")

        # Build tool config
        file_search_config = types.FileSearch(
            file_search_store_names=store_names
        )

        # Add metadata filter if provided
        if metadata_filter:
            file_search_config.metadata_filter = metadata_filter

        # Generate response
        response = self.client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(
                tools=[types.Tool(file_search=file_search_config)]
            )
        )

        # Extract citations and grounding metadata
        result = {
            'text': response.text,
            'citations': [],
            'grounding_metadata': None
        }

        if hasattr(response.candidates[0], 'grounding_metadata'):
            result['grounding_metadata'] = response.candidates[0].grounding_metadata

            # Extract citation details
            if result['grounding_metadata']:
                for chunk in result['grounding_metadata'].grounding_chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        result['citations'].append({
                            'source': chunk.web.uri,
                            'title': chunk.web.title if hasattr(chunk.web, 'title') else None
                        })

        return result

    def list_all_stores(self):
        """List all File Search stores in your account"""
        print("\n📚 Your File Search Stores:")
        for store in self.client.file_search_stores.list():
            print(f"  • {store.display_name or store.name}")

    def get_store_info(self, category: str):
        """Get detailed info about a specific store"""
        if category not in self.stores:
            raise ValueError(f"Store '{category}' not found")

        store = self.client.file_search_stores.get(name=self.stores[category])
        return store


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = GBDFileSearchManager()

    # Create GBD-organized stores
    stores = manager.create_gbd_stores()

    # Example: Upload causes data
    # causes_files = [
    #     '/path/to/gbd_2023/causes/IHME_GBD_2023_CAUSES_GLOBAL.csv',
    #     '/path/to/gbd_2023/causes/IHME_GBD_2023_CAUSES_USA.csv',
    # ]
    # manager.upload_csv_batch(
    #     file_paths=causes_files,
    #     category='causes',
    #     custom_metadata=[
    #         {"key": "dataset", "string_value": "GBD 2023"},
    #         {"key": "version", "string_value": "2023.12"}
    #     ]
    # )

    # Example: Query with metadata filtering
    # result = manager.query_with_citations(
    #     question="What are the top 10 causes of death globally in 2023?",
    #     categories=['causes'],
    #     metadata_filter="year=2023 AND geography=global"
    # )
    # print(result['text'])
    # print(f"\nCitations: {result['citations']}")
