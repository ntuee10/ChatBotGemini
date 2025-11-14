# Schema Consistency Guide: Ensuring Ground Truth Integrity

## The Problem

You identified a critical concern: **GBD CSV files may have inconsistent column names across different files:**

```
File A: deaths | age_group | location
File B: mortality | age_category | country
File C: death_count | age_range | geography

→ Same data, different names!
```

Without standardization, this causes:
- ❌ Semantic search misses relevant data
- ❌ Inconsistent answers across similar files
- ❌ Difficulty aggregating multi-file results
- ❌ Broken ground truth integrity

---

## Can Gemini File Search Handle This Alone?

**Answer: NO - Not reliably enough for research-grade work.**

While Gemini has semantic understanding ("deaths" ≈ "mortality"), it:
- ❌ Cannot guarantee consistent field extraction
- ❌ May miss exact column matches
- ❌ Struggles with domain-specific mappings (GBD hierarchy)
- ❌ Cannot enforce schema validation

**For ground truth data, you need EXPLICIT schema management.**

---

## The Solution: Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: GBD Schema Mapper (Before Upload)                │
│  • Standardizes column names (deaths ← mortality, death_count)
│  • Validates schema against GBD standards                  │
│  • Maps to gbd_mapping package conventions                 │
│  • Generates column mapping metadata                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Gemini File Search (Vector Database)             │
│  • Stores standardized CSVs with embeddings                │
│  • Semantic search with consistent terminology             │
│  • Column mapping stored as metadata                       │
│  • Citations back to source files                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: Semantic Layer (Query Translation)               │
│  • Translates user queries to standard terminology         │
│  • Validates extracted data against schema                 │
│  • Ensures ground truth consistency                        │
│  • Provides citation verification                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation: Step-by-Step

### Step 1: Validate and Standardize CSVs Before Upload

```python
from gbd_schema_mapper import GBDSchemaMapper

mapper = GBDSchemaMapper()

# Validate original CSV
validation = mapper.validate_csv_schema('IHME_GBD_2023_CAUSES_ORIGINAL.csv')

print(f"Valid: {validation['valid']}")
print(f"Columns: {validation['standardized_columns']}")
print(f"Issues: {validation['recommendations']}")

# Standardize and prepare for upload
standardized_file, metadata = mapper.prepare_for_file_search(
    csv_path='IHME_GBD_2023_CAUSES_ORIGINAL.csv',
    output_path='IHME_GBD_2023_CAUSES_STANDARDIZED.csv'
)

print(f"\n✅ Standardized file: {standardized_file}")
print(f"📋 Metadata: {metadata}")
```

**Output Example:**
```
Valid: True
Columns: ['year', 'location', 'age_group', 'sex', 'cause', 'deaths', 'dalys']

✅ Standardized file: IHME_GBD_2023_CAUSES_STANDARDIZED.csv
📋 Metadata: [
  {"key": "schema_standardized", "string_value": "true"},
  {"key": "dimensions", "string_value": "year, location, age_group, sex, cause"},
  {"key": "metrics", "string_value": "deaths, dalys"},
  {"key": "column_mapping", "string_value": "{\"death_count\": \"deaths\", \"country\": \"location\"}"}
]
```

### Step 2: Upload Standardized Files to Gemini File Search

```python
from gemini_file_search import GBDFileSearchManager
from gbd_schema_mapper import GBDSchemaMapper

manager = GBDFileSearchManager()
mapper = GBDSchemaMapper()

# Create stores
stores = manager.create_gbd_stores()

# Process and upload each CSV
csv_files = Path('gbd_data/causes').glob('*.csv')

for csv_file in csv_files:
    # 1. Standardize schema
    std_file, schema_metadata = mapper.prepare_for_file_search(str(csv_file))

    # 2. Upload standardized version
    manager.upload_csv_batch(
        file_paths=[std_file],
        category='causes',
        custom_metadata=schema_metadata  # ← Schema metadata included!
    )

    print(f"✅ Uploaded: {csv_file.name} (standardized)")
```

**Key Point:** File Search now has:
- ✅ Standardized column names
- ✅ Column mapping metadata
- ✅ Schema validation confirmation

### Step 3: Query with Schema Awareness

```python
from semantic_layer import GBDSemanticLayer

layer = GBDSemanticLayer()

# Query uses standardized terminology automatically
result = layer.ask_question(
    question="What were the deaths from cardiovascular disease in USA in 2023?",
    categories=['causes'],
    year=2023
)

# The answer is grounded in files with STANDARDIZED schemas
print(result['answer'])
print(f"\nSource: {result['sources'][0]['file']}")
print(f"Schema: {result['sources'][0].get('metadata', {}).get('schema_standardized')}")
```

---

## Column Name Standardization

The `GBDSchemaMapper` maps all variations to standard GBD terminology:

### Metrics

| Variations | Standard Name |
|-----------|---------------|
| deaths, death, mortality, mortality_count, death_count | **deaths** |
| dalys, daly, disability_adjusted_life_years | **dalys** |
| ylds, yld, years_lived_with_disability | **ylds** |
| ylls, yll, years_of_life_lost | **ylls** |
| prevalence, prev, prevalence_rate | **prevalence** |
| incidence, inc, cases, new_cases | **incidence** |

### Dimensions

| Variations | Standard Name |
|-----------|---------------|
| year, year_id, time, period | **year** |
| location, location_name, country, geography, region | **location** |
| age_group, age, age_category, age_range | **age_group** |
| sex, gender, sex_name | **sex** |
| cause, cause_name, gbd_cause | **cause** |
| risk, risk_name, risk_factor, rei | **risk** |

### Statistical Columns

| Variations | Standard Name |
|-----------|---------------|
| mean, val, value, estimate | **mean** |
| lower, lower_bound, lower_ui, lower_95 | **lower** |
| upper, upper_bound, upper_ui, upper_95 | **upper** |

---

## Integration with GBD Mapping Package

If you have access to the `gbd_mapping` package (requires IHME credentials):

```python
from gbd_schema_mapper import GBDSchemaMapper

mapper = GBDSchemaMapper()

# The mapper can use gbd_mapping to:
# 1. Validate cause/risk/covariate IDs
# 2. Map cause names to standardized hierarchy
# 3. Ensure etiology-sequela relationships are correct

# Example: Validate cause names
mapper.validate_cause_names(['Diabetes mellitus', 'Cardiovascular diseases'])
# → Maps to GBD cause hierarchy

# Example: Get cause metadata
cause_info = mapper.get_gbd_cause_metadata('Diabetes mellitus')
# → Returns: parent causes, GBD ID, hierarchy level, etc.
```

---

## Schema Validation Report

Generate a comprehensive schema report across all your files:

```python
from gbd_schema_mapper import GBDSchemaMapper
from pathlib import Path

mapper = GBDSchemaMapper()

# Get all CSV files
all_csvs = list(Path('gbd_data').rglob('*.csv'))

# Generate schema documentation
schema_report = mapper.generate_schema_documentation(all_csvs)

# Save report
with open('gbd_schema_validation_report.md', 'w') as f:
    f.write(schema_report)

print("✅ Schema validation report saved!")
```

**Example Report Output:**

```markdown
# GBD Dataset Schema Analysis

## IHME_GBD_2023_CAUSES_MORTALITY_GLOBAL.csv

**Status:** ✅ Valid

- Rows: 1,245,789
- Columns: 12
- Dimensions: year, location, age_group, sex, cause
- Metrics: deaths, dalys

**Column Mapping:**
- `death_count` → `deaths`
- `country` → `location`
- `age_category` → `age_group`

---

## IHME_GBD_2023_RISKS_DALYS_USA.csv

**Status:** ❌ Issues Found

- Rows: 543,210
- Columns: 15
- Dimensions: year, location, age_group
- Metrics: dalys

**Unmapped Columns:** weird_col_1, unknown_metric_x

**Recommendations:**
- Missing sex dimension. Consider adding.
- Unmapped columns found. Review and rename to standard names.
```

---

## Best Practices

### 1. Always Validate Before Upload

```python
# DON'T: Upload raw files directly
manager.upload_csv_batch(file_paths=['raw_data.csv'], ...)  # ❌

# DO: Validate and standardize first
std_file, metadata = mapper.prepare_for_file_search('raw_data.csv')
manager.upload_csv_batch(file_paths=[std_file], ...)  # ✅
```

### 2. Include Schema Metadata

```python
# Upload with schema metadata
manager.upload_csv_batch(
    file_paths=[std_file],
    category='causes',
    custom_metadata=[
        *schema_metadata,  # ← Include schema info!
        {"key": "validated", "string_value": "true"},
        {"key": "upload_date", "string_value": "2025-11-14"}
    ]
)
```

### 3. Document Your Schema

```python
# Generate schema report BEFORE upload
schema_report = mapper.generate_schema_documentation(all_csv_files)

# Review it manually - catch issues early!
with open('schema_validation.md', 'w') as f:
    f.write(schema_report)
```

### 4. Use Standard Terminology in Queries

```python
# GOOD: Use standardized terms
result = layer.ask_question(
    "What were the deaths from diabetes?",  # ✅ 'deaths' is standard
    categories=['causes']
)

# AVOID: Non-standard terms (but will still work via semantic search)
result = layer.ask_question(
    "What was the mortality count from diabetes?",  # ⚠️  Less precise
    categories=['causes']
)
```

---

## FAQ

### Q: Do I need to standardize if my CSVs already have consistent naming?

**A:** Run validation anyway! It confirms your schema and adds metadata that improves search accuracy.

```python
validation = mapper.validate_csv_schema('my_file.csv')
if validation['valid'] and not validation['recommendations']:
    print("✅ Schema already good - but still upload with metadata!")
```

### Q: What if I can't access the gbd_mapping package?

**A:** The `GBDSchemaMapper` works without it! It uses fallback mappings based on common GBD terminology.

### Q: Can I add custom column mappings?

**A:** Yes! Extend the mapper:

```python
mapper = GBDSchemaMapper()

# Add custom mappings
mapper.COLUMN_MAPPINGS['my_custom_metric'] = [
    'my_custom_metric', 'custom_var', 'special_measure'
]

# Rebuild reverse mapping
mapper.reverse_mapping = mapper._build_reverse_mapping()
```

### Q: What happens to unmapped columns?

**A:** They're preserved in the uploaded file and flagged in metadata:

```json
{
  "key": "unmapped_columns",
  "string_value": "col_x, col_y, col_z"
}
```

You can still search them - Gemini's semantic search handles unmapped columns, just less precisely.

---

## Verification: Ensuring Ground Truth

After upload, verify ground truth integrity:

```python
# 1. Query for specific data
result = layer.ask_question(
    "What were the deaths from diabetes in USA in 2023?",
    categories=['causes']
)

# 2. Check citations
print(f"Sources: {result['sources']}")

# 3. Verify schema metadata
for source in result['sources']:
    print(f"File: {source['file']}")
    print(f"Schema validated: {source.get('metadata', {}).get('schema_standardized')}")
    print(f"Column mapping: {source.get('metadata', {}).get('column_mapping')}")

# 4. Cross-check answer against original CSV
# Load the cited source file and verify the numbers match
```

---

## Summary

| Aspect | Without Schema Mapper | With Schema Mapper |
|--------|----------------------|-------------------|
| Column consistency | ❌ Varies by file | ✅ Standardized |
| Query reliability | ⚠️  Semantic search only | ✅ Schema + semantic |
| Ground truth verification | ❌ Difficult | ✅ Easy (metadata) |
| Multi-file aggregation | ❌ Unreliable | ✅ Consistent |
| GBD mapping integration | ❌ No | ✅ Yes (optional) |
| Data quality validation | ❌ Manual | ✅ Automated |

---

## Recommendation

**YES - Gemini File Search CAN handle GBD data reliably, BUT:**

✅ **USE** the `GBDSchemaMapper` to standardize schemas BEFORE upload
✅ **VALIDATE** all CSVs and generate schema reports
✅ **INCLUDE** schema metadata when uploading to File Search
✅ **DOCUMENT** your column mappings and validation process

This ensures:
- ✅ Ground truth integrity is maintained
- ✅ Queries return consistent results
- ✅ Multi-file aggregation works correctly
- ✅ Citations can be verified against source data

**The combination of Schema Mapper + File Search + Semantic Layer gives you research-grade reliability!**
