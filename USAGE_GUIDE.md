# GBD Semantic Layer - Complete Usage Guide

## Architecture Overview

This system uses **Gemini File Search as a Vector Database** for your GBD CSV files, not local file loading. This approach is optimal for large datasets (20GB+) and files up to 250MB.

---

## Setup Process (One-Time)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Gemini API

```bash
# Get API key from: https://aistudio.google.com/apikey
export GOOGLE_API_KEY='your-api-key-here'

# Or create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

### Step 3: Verify Your Gemini Subscription Tier

**CRITICAL: Check your tier at https://ai.google.dev/pricing**

- Free: 1 GB → ❌ Too small for 20GB dataset
- Tier 1: 10 GB → ❌ Too small
- **Tier 2: 100 GB → ✅ Perfect (20GB × 3 = 60GB used)**
- Tier 3: 1 TB → ✅ Plenty of room

*Note: Storage used = Input size × 3 (due to embeddings)*

---

## Phase 1: Upload CSV Files to Vector Database

### Prepare Your CSV Files

```bash
# Organize your GBD files
gbd_data/
├── causes/
│   ├── IHME_GBD_2023_CAUSES_GLOBAL.csv (150MB)
│   ├── IHME_GBD_2023_CAUSES_USA.csv (250MB) ⚠️ Will be auto-split
│   └── ...
├── risks/
│   ├── IHME_GBD_2023_RISKS_GLOBAL.csv
│   └── ...
├── covariates/
└── ...
```

### Upload Script

```python
from gemini_file_search import GBDFileSearchManager
import os
from pathlib import Path

# Initialize manager
manager = GBDFileSearchManager(api_key=os.getenv('GOOGLE_API_KEY'))

# Create organized stores (one for each GBD category)
print("Creating File Search stores...")
stores = manager.create_gbd_stores()

# Upload causes data
print("\nUploading CAUSES data...")
causes_dir = Path("gbd_data/causes")
causes_files = list(causes_dir.glob("*.csv"))

# The manager automatically:
# 1. Splits files >100MB
# 2. Extracts metadata from filenames
# 3. Uploads to correct store
# 4. Chunks and embeds data
# 5. Stores in vector DB
manager.upload_csv_batch(
    file_paths=[str(f) for f in causes_files],
    category='causes',
    custom_metadata=[
        {"key": "dataset", "string_value": "GBD 2023"},
        {"key": "upload_date", "string_value": "2025-11-14"}
    ]
)

# Repeat for other categories
print("\nUploading RISKS data...")
risks_files = list(Path("gbd_data/risks").glob("*.csv"))
manager.upload_csv_batch(
    file_paths=[str(f) for f in risks_files],
    category='risks',
    custom_metadata=[{"key": "dataset", "string_value": "GBD 2023"}]
)

# ... repeat for covariates, etiologies, sequelae

print("\n✅ All data uploaded to vector database!")
print("💾 Total storage used: ~60GB (for 20GB of CSV files)")
```

**Important**: This is a **one-time upload**. After this, your CSV files are permanently in the vector DB until you delete them.

---

## Phase 2: Query the Vector Database (Daily Research)

### Basic Querying

```python
from semantic_layer import GBDSemanticLayer

# Initialize semantic layer
layer = GBDSemanticLayer()

# Ask questions - data comes from vector DB, not local files!
result = layer.ask_question(
    question="What were the top 10 causes of death globally in 2023?",
    categories=['causes'],
    year=2023,
    region='global'
)

print(result['answer'])
print(f"\nCitations: {result['sources']}")
```

**Output Example:**
```
The top 10 causes of death globally in 2023 were:
1. Ischaemic heart disease - 9.1 million deaths
2. Stroke - 6.2 million deaths
3. Chronic obstructive pulmonary disease - 3.2 million deaths
...

Citations:
- IHME_GBD_2023_CAUSES_GLOBAL.csv (rows 1245-1389)
- IHME_GBD_2023_CAUSES_SUMMARY.csv (table 3)
```

### Advanced Filtering with Metadata

```python
# Query specific subsets using metadata filters
result = layer.ask_question(
    question="How did cardiovascular disease deaths change from 2019 to 2023?",
    categories=['causes'],
    # This filters the vector DB search to only relevant chunks
    metadata_filter="year IN [2019, 2020, 2021, 2022, 2023] AND category=causes"
)
```

---

## Phase 3: Advanced Analytics on Retrieved Data

### Approach A: Extract Data from Gemini, Then Analyze

```python
import pandas as pd
from advanced_analytics import AdvancedGBDAnalytics

# 1. Get data from vector DB via semantic query
result = layer.ask_question(
    question="""
    Extract diabetes prevalence data for USA from 2015-2023 as a table.
    Include columns: year, prevalence_per_100k, age_standardized_rate
    """,
    categories=['covariates'],
    region='USA'
)

# 2. Parse the returned data into DataFrame
# (Gemini can return structured data if you ask for it!)
data_str = result['answer']  # Contains table in markdown or CSV format
df = pd.read_csv(io.StringIO(data_str))  # Parse if CSV format

# 3. Run advanced analytics
engine = AdvancedGBDAnalytics(df, date_column='year')

# Forecast next 5 years
forecast = engine.prophet_forecast(
    metric='prevalence_per_100k',
    periods=5,
    freq='Y'
)

print(f"Predicted 2028 prevalence: {forecast['final_forecast']:.1f}")
print(f"Change from 2023: {forecast['percent_change']:.1f}%")
```

### Approach B: Integrated Analysis with Context

```python
# Let the semantic layer handle everything

# Causal Impact: Did policy X reduce deaths?
causal_report = layer.analyze_intervention_impact(
    data=df,  # Small extracted dataset from vector DB
    metric='deaths',
    intervention_date='2020-03-15',
    intervention_name='COVID-19 Lockdown',
    ask_gemini_for_context=True  # Gets background from vector DB
)

print(causal_report['grounded_context'])  # Gemini's context
print(causal_report['statistical_analysis'])  # CausalImpact results
print(causal_report['interpretation'])  # Combined insights
```

---

## Phase 4: Generate Research Reports

```python
from semantic_layer import GBDSemanticLayer

layer = GBDSemanticLayer()

# Generate comprehensive report
report = layer.generate_research_report(
    research_question="What is the burden of diabetes in low-income countries, and what are the projected trends?",
    data=extracted_df,  # Small dataset from vector DB
    analyses=['descriptive', 'temporal', 'forecast'],
    output_format='markdown'
)

# Save report
with open('diabetes_burden_report.md', 'w') as f:
    f.write(report)

print("✅ Report generated with citations to source CSV files!")
```

**Generated Report Includes:**
- Executive summary (from Gemini vector DB)
- Descriptive statistics
- Temporal trend analysis with decomposition
- 5-year forecast with confidence intervals
- Professional visualizations
- **Citations to original CSV files**

---

## Handling 250MB CSV Files

### Automatic Splitting

When you upload a 250MB file, the `GBDFileSearchManager` automatically:

```python
# This happens internally - you don't need to do anything!

# Input: IHME_GBD_2023_CAUSES_USA.csv (250MB)
#   ↓
# Automatically split into:
#   IHME_GBD_2023_CAUSES_USA_part1.csv (95MB)
#   IHME_GBD_2023_CAUSES_USA_part2.csv (95MB)
#   IHME_GBD_2023_CAUSES_USA_part3.csv (60MB)
#   ↓
# Each part uploaded separately
#   ↓
# Chunked and embedded
#   ↓
# Stored in vector DB
#   ↓
# When you query, Gemini searches ALL parts seamlessly!
```

### Manual Pre-Splitting (Optional)

If you want control over splitting:

```python
from gemini_file_search import GBDFileSearchManager

manager = GBDFileSearchManager()

# Split a large file
large_file = 'gbd_data/causes/IHME_GBD_2023_CAUSES_USA.csv'
split_files = manager.split_large_csv(large_file, max_size_mb=95)

print(f"Split into {len(split_files)} files:")
for f in split_files:
    print(f"  - {f}")
```

---

## Cost Estimation

### One-Time Indexing Cost

```
20 GB of CSV data ≈ 5-10 billion tokens (varies by data density)

Indexing cost:
  - $0.15 per 1 million tokens
  - 5,000-10,000 million tokens
  - Total: $750 - $1,500 (ONE TIME)

Storage cost:
  - FREE (Gemini doesn't charge for storage)

Query cost:
  - FREE (embeddings at query time are free)
  - Only pay for Gemini model usage (regular pricing)
```

### Ongoing Costs

- **Queries**: Standard Gemini API pricing
  - gemini-2.5-flash: $0.075 / 1M input tokens
  - gemini-2.5-pro: $1.25 / 1M input tokens

---

## Example Research Workflows

### Workflow 1: Causal Analysis

**Question**: "Did COVID-19 lockdowns reduce traffic deaths?"

```python
# 1. Ask vector DB for context
context = layer.ask_question(
    "What is known about traffic deaths during COVID-19 lockdowns?",
    categories=['causes'],
    year=2020
)

# 2. Get relevant data
data_query = layer.ask_question(
    "Extract monthly traffic death counts for USA from 2018-2022",
    categories=['causes']
)

# 3. Parse into DataFrame (Gemini returns structured data)
df = parse_gemini_table(data_query['answer'])

# 4. Run causal impact analysis
causal = layer.analyze_intervention_impact(
    data=df,
    metric='traffic_deaths',
    intervention_date='2020-03-15',
    intervention_name='COVID-19 Lockdown'
)

# 5. Get professional report with citations
print(causal['interpretation'])
```

### Workflow 2: Predictive Analysis

**Question**: "What will diabetes prevalence be in 2030?"

```python
# 1. Extract historical data from vector DB
result = layer.ask_question(
    "Provide annual diabetes prevalence globally from 2000-2023",
    categories=['covariates']
)

df = parse_gemini_table(result['answer'])

# 2. Forecast with Prophet
forecast = layer.forecast_with_context(
    data=df,
    metric='diabetes_prevalence',
    periods=7,  # 2024-2030
    freq='Y',
    ask_gemini_for_trends=True  # Get historical context
)

print(f"2030 Prediction: {forecast['forecast_results']['final_forecast']}")
print(f"Grounded Context: {forecast['grounded_context']}")
```

### Workflow 3: Comparative Analysis

**Question**: "How do high-income vs low-income countries compare on malaria burden?"

```python
# 1. Ask vector DB for background
background = layer.ask_question(
    "Summarize known differences in malaria burden between high-income and low-income countries",
    categories=['causes']
)

# 2. Get comparison data
data = layer.ask_question(
    "Extract malaria deaths per 100k by income level for 2023",
    categories=['causes'],
    year=2023
)

df = parse_gemini_table(data['answer'])

# 3. Run A/B test
comparison = layer.compare_groups(
    data=df,
    metric='deaths_per_100k',
    group_column='income_level',
    group_a='High income',
    group_b='Low income',
    ask_gemini_for_background=True
)

print(comparison['interpretation'])
print(f"Effect size: {comparison['statistical_test']['effect_size']}")
```

---

## FAQ

### Q: Do I need to keep the original CSV files after uploading?

**A:** No! Once uploaded to Gemini File Search, the data is in the vector database permanently (until you delete it). You can archive or delete the original CSVs.

### Q: How do I update data when new GBD releases come out?

**A:** Simply upload the new CSV files to a new store (e.g., `gbd-2024-causes`) or update the existing store.

### Q: Can I mix CSV files from different years in one store?

**A:** Yes, but use metadata tags to filter:

```python
manager.upload_csv_batch(
    files=['gbd_2021_data.csv'],
    category='causes',
    custom_metadata=[{"key": "year", "numeric_value": 2021}]
)

# Later, query only 2021 data
layer.ask_question(
    "Top causes in 2021",
    metadata_filter="year=2021"
)
```

### Q: What if I want to run complex pandas operations?

**A:** Extract a small, relevant subset from the vector DB first:

```python
# Ask Gemini to give you exactly what you need
result = layer.ask_question(
    "Extract all diabetes data for USA, ages 50-70, years 2015-2023. Return as CSV format.",
    categories=['covariates']
)

# Parse into DataFrame
df = pd.read_csv(io.StringIO(result['answer']))

# Now run any pandas operations you want
filtered = df[df['age_group'] == '50-54']
aggregated = df.groupby('year')['prevalence'].mean()
# etc...
```

---

## Next Steps

1. **Upload your 20GB of GBD CSV files** to Gemini File Search
2. **Test semantic queries** to verify data is accessible
3. **Run pilot analyses** on a specific research question
4. **Generate your first research report** with citations

**Remember**: The CSV files live in the vector database, not on your local machine. You query them via natural language and semantic search, which is much more powerful than traditional pandas operations!
