"""
Demonstration: How Filename Metadata Powers Semantic Search

This shows how extracting rich metadata from GBD filenames enables
powerful filtering and semantic understanding.
"""

from gemini_file_search import GBDFileSearchManager
import json

# Example GBD filenames
example_filenames = [
    "IHME_GBD_2023_CAUSES_MORTALITY_AGE_STANDARDIZED_GLOBAL_2023.csv",
    "IHME_GBD_2021_RISKS_DALYS_BOTH_SEXES_USA_2021.csv",
    "GBD_2023_COVARIATES_PREVALENCE_DIABETES_NATIONAL_INDIA.csv",
    "IHME_GBD_2023_CAUSES_DEATHS_CARDIOVASCULAR_REGIONAL_AFRICA.csv",
    "GBD_2019_RISKS_YLLs_SMOKING_HIGH_INCOME_2019.csv",
    "IHME_GBD_2023_SEQUELAE_YLDs_STROKE_GLOBAL_BOTH_SEXES.csv",
    "GBD_2023_CAUSES_INCIDENCE_MALARIA_LOW_INCOME_UNDER5.csv",
    "IHME_GBD_2021_ETIOLOGIES_MORTALITY_TUBERCULOSIS_IND_2021.csv",
]

manager = GBDFileSearchManager()

print("=" * 80)
print("DEMONSTRATION: Filename Metadata Extraction for GBD Files")
print("=" * 80)
print("\nThis shows how rich metadata extracted from filenames enables powerful")
print("semantic search and filtering across 20GB of GBD data.\n")

for i, filename in enumerate(example_filenames, 1):
    print(f"\n{'=' * 80}")
    print(f"EXAMPLE {i}: {filename}")
    print(f"{'=' * 80}")

    # Extract metadata
    metadata = manager.extract_metadata_from_filename(filename)

    # Organize by category
    metadata_dict = {}
    for item in metadata:
        key = item['key']
        value = item.get('string_value') or item.get('numeric_value')
        if key not in metadata_dict:
            metadata_dict[key] = value

    # Display in readable format
    important_keys = [
        'organization', 'dataset', 'year', 'category', 'metric',
        'geography_level', 'country', 'condition', 'age_group',
        'sex', 'age_adjustment', 'income_level', 'file_description', 'tags'
    ]

    for key in important_keys:
        if key in metadata_dict:
            print(f"  {key:20s}: {metadata_dict[key]}")

print("\n" + "=" * 80)
print("HOW THIS ENABLES POWERFUL QUERIES")
print("=" * 80)

print("""
With this metadata, you can ask highly specific questions:

1. TEMPORAL QUERIES:
   • "What was the change in diabetes prevalence from 2019 to 2023?"
   → Filters: year IN [2019, 2023] AND condition=Diabetes

2. GEOGRAPHIC QUERIES:
   • "Compare cardiovascular disease burden in USA vs India"
   → Filters: country IN [USA, India] AND condition=Cardiovascular

3. DEMOGRAPHIC QUERIES:
   • "What are the top causes of death in children under 5?"
   → Filters: age_group="Under 5 years" AND category=causes

4. METHODOLOGICAL QUERIES:
   • "Show age-standardized mortality rates for all countries"
   → Filters: age_adjustment="Age Standardized" AND metric=deaths

5. COMPLEX MULTI-FILTER QUERIES:
   • "What risk factors contribute most to DALYs in high-income countries for females?"
   → Filters: category=risks AND metric=dalys AND income_level="High income" AND sex=female

6. SEMANTIC SEARCHES:
   • "What is the burden of mental health conditions globally?"
   → Gemini searches tags, conditions, and file descriptions for mental health terms
   → Finds files with: depression, anxiety, schizophrenia, etc.

7. COMPARATIVE ANALYSES:
   • "How do YLLs vs YLDs differ for chronic diseases?"
   → Filters: metric IN [ylls, ylds] AND tags CONTAINS "chronic"
""")

print("\n" + "=" * 80)
print("EXAMPLE METADATA FILTER QUERIES")
print("=" * 80)

filters = [
    ("Files from 2023 only", "year=2023"),
    ("Diabetes data for all countries", "condition='Diabetes mellitus'"),
    ("Global mortality data", "geography_level=global AND metric=deaths"),
    ("USA cardiovascular risk data", "country='United States' AND category=risks AND condition='Cardiovascular diseases'"),
    ("High-income country data for both sexes", "income_level='High income' AND sex=both"),
    ("Age-standardized rates only", "age_adjustment='Age Standardized'"),
    ("Data with disability metrics", "tags CONTAINS 'disability'"),
]

for desc, filter_expr in filters:
    print(f"\n{desc}:")
    print(f"  Filter: {filter_expr}")

print("\n" + "=" * 80)
print("BENEFITS FOR RESEARCHERS")
print("=" * 80)

print("""
✅ NO MANUAL TAGGING REQUIRED
   • Metadata extracted automatically from existing filenames
   • No need to create separate metadata files

✅ HANDLES 250MB FILES
   • Files >100MB automatically split into chunks
   • All chunks share the same metadata
   • Semantic search works seamlessly across all chunks

✅ PRECISE FILTERING
   • Find exactly the data you need from 20GB of files
   • Combine multiple filters for complex queries
   • Fast semantic search (no need to scan all files)

✅ GROUND TRUTH VERIFICATION
   • Every answer includes citations back to source files
   • Verify which specific CSV provided the data
   • Track data lineage for publications

✅ NATURAL LANGUAGE QUERIES
   • Ask questions in plain English
   • Gemini translates to semantic search + metadata filters
   • No need to write SQL or complex filters manually

Example workflow:
   1. Upload 20GB of GBD CSVs (one time)
   2. Ask: "What are the trends in diabetes mortality in India from 2015-2023?"
   3. Gemini automatically:
      a) Filters: country=India AND condition=Diabetes AND year BETWEEN 2015-2023
      b) Searches semantic content for mortality trends
      c) Returns answer with citations to specific CSV files
   4. You get the answer in seconds, not hours of pandas coding!
""")

print("\n" + "=" * 80)
print("✅ DEMONSTRATION COMPLETE")
print("=" * 80)
print("\nNext step: Upload your GBD CSV files using the batch upload script!")
print("See: USAGE_GUIDE.md for complete instructions\n")
