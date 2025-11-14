# Quick Start Guide: GBD Semantic Layer

Get up and running with the GBD Semantic Layer in 15 minutes.

---

## What You'll Build

A powerful semantic search and analytics system over 20GB of GBD CSV files that:

1. ✅ Stores data in **Gemini's vector database** (not local files)
2. ✅ Answers questions with **citations to source CSVs**
3. ✅ Runs **advanced analytics** (causal, predictive, A/B tests)
4. ✅ Generates **publication-ready reports** with professional visualizations

---

## Prerequisites

- **Python 3.8+**
- **Gemini API key** (Tier 2 or 3 subscription for 20GB data)
- **GBD 2023 CSV files** (~20GB, files up to 250MB)

---

## Step 1: Installation (2 minutes)

```bash
# Clone or navigate to the repository
cd csv-data-summarizer-claude-skill

# Install dependencies
pip install -r requirements.txt

# Set up Gemini API key
export GOOGLE_API_KEY='your-api-key-here'

# Or create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

**Get API Key:** https://aistudio.google.com/apikey
**Check Tier:** https://ai.google.dev/pricing (need Tier 2 or 3)

---

## Step 2: Organize Your CSV Files (5 minutes)

```bash
# Create directory structure
mkdir -p gbd_data/{causes,risks,covariates,etiologies,sequelae}

# Move your GBD CSV files into appropriate categories
# Example:
mv IHME_GBD_2023_CAUSES_*.csv gbd_data/causes/
mv IHME_GBD_2023_RISKS_*.csv gbd_data/risks/
mv IHME_GBD_2023_COVARIATES_*.csv gbd_data/covariates/
# etc.
```

**Note:** Files with informative names work best:
- ✅ Good: `IHME_GBD_2023_CAUSES_MORTALITY_GLOBAL_2023.csv`
- ⚠️  Less ideal: `data1.csv`, `export_final_v2.csv`

The system extracts metadata from filenames automatically!

---

## Step 3: Upload to Vector Database (One-Time, ~30-60 minutes)

Create `upload_gbd_data.py`:

```python
#!/usr/bin/env python3
"""
One-time upload script for GBD data to Gemini File Search
"""

from gemini_file_search import GBDFileSearchManager
from pathlib import Path
import os

# Initialize manager
manager = GBDFileSearchManager(api_key=os.getenv('GOOGLE_API_KEY'))

# Create stores (one for each GBD category)
print("📦 Creating File Search stores...")
stores = manager.create_gbd_stores()

# Upload each category
categories = ['causes', 'risks', 'covariates', 'etiologies', 'sequelae']

for category in categories:
    data_dir = Path(f"gbd_data/{category}")

    if not data_dir.exists():
        print(f"⏭️  Skipping {category} (directory not found)")
        continue

    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        print(f"⏭️  Skipping {category} (no CSV files found)")
        continue

    print(f"\n📤 Uploading {len(csv_files)} files to '{category}' store...")

    manager.upload_csv_batch(
        file_paths=[str(f) for f in csv_files],
        category=category,
        custom_metadata=[
            {"key": "dataset", "string_value": "GBD 2023"},
            {"key": "upload_date", "string_value": "2025-11-14"}
        ]
    )

print("\n✅ Upload complete! Your data is now in the vector database.")
print("💾 Storage used: ~60GB (20GB data + embeddings)")
print("💰 One-time indexing cost: ~$750-$1,500")
print("🎉 You can now query your data with semantic search!")
```

Run it:

```bash
python upload_gbd_data.py
```

**What happens:**
- Files >100MB automatically split into chunks
- Metadata extracted from filenames
- Data chunked, embedded, and indexed
- Stored in Gemini's vector database

**This is a ONE-TIME operation!** Once uploaded, your data stays in the vector DB until you delete it.

---

## Step 4: Query Your Data (Instant)

Create `query_example.py`:

```python
from semantic_layer import GBDSemanticLayer

# Initialize semantic layer
layer = GBDSemanticLayer()

# Ask questions - answers come from the vector database!
result = layer.ask_question(
    question="What were the top 10 causes of death globally in 2023?",
    categories=['causes'],
    year=2023
)

print("QUESTION:")
print(result['question'])
print("\nANSWER:")
print(result['answer'])
print("\nCITATIONS:")
for source in result['sources']:
    print(f"  • {source['file']}")
```

Run it:

```bash
python query_example.py
```

**Example Output:**
```
QUESTION:
What were the top 10 causes of death globally in 2023?

ANSWER:
The top 10 causes of death globally in 2023 were:
1. Ischaemic heart disease - 9.1 million deaths
2. Stroke - 6.2 million deaths
3. Chronic obstructive pulmonary disease - 3.2 million deaths
4. Lower respiratory infections - 2.6 million deaths
5. Neonatal conditions - 1.9 million deaths
...

CITATIONS:
  • IHME_GBD_2023_CAUSES_MORTALITY_GLOBAL_2023.csv
  • IHME_GBD_2023_CAUSES_AGE_STANDARDIZED_GLOBAL.csv
```

---

## Step 5: Advanced Analytics (5 minutes)

### Example 1: Forecast Future Trends

```python
from semantic_layer import GBDSemanticLayer
import pandas as pd
import io

layer = GBDSemanticLayer()

# 1. Get historical data from vector DB
result = layer.ask_question(
    question="""
    Extract annual diabetes prevalence per 100,000 for USA from 2015-2023.
    Format as CSV with columns: year,prevalence
    """,
    categories=['covariates'],
    region='USA'
)

# 2. Parse into DataFrame
df = pd.read_csv(io.StringIO(result['answer']))

# 3. Forecast next 5 years
forecast = layer.forecast_with_context(
    data=df,
    metric='prevalence',
    periods=5,
    freq='Y',
    ask_gemini_for_trends=True
)

print(f"2028 Prediction: {forecast['forecast_results']['final_forecast']:.1f}")
print(f"Change: {forecast['forecast_results']['percent_change']:.1f}%")
```

### Example 2: Causal Impact Analysis

```python
# Did COVID-19 lockdowns reduce traffic deaths?

# Get data from vector DB
result = layer.ask_question(
    "Extract monthly traffic death counts for USA from 2018-2022",
    categories=['causes']
)

df = parse_gemini_response(result['answer'])

# Analyze intervention impact
causal = layer.analyze_intervention_impact(
    data=df,
    metric='traffic_deaths',
    intervention_date='2020-03-15',
    intervention_name='COVID-19 Lockdown',
    ask_gemini_for_context=True
)

print(causal['interpretation'])
```

### Example 3: A/B Testing

```python
# Compare malaria burden: high-income vs low-income countries

result = layer.ask_question(
    "Extract malaria deaths per 100k by income level for 2023",
    categories=['causes'],
    year=2023
)

df = parse_gemini_response(result['answer'])

comparison = layer.compare_groups(
    data=df,
    metric='deaths_per_100k',
    group_column='income_level',
    group_a='High income',
    group_b='Low income'
)

print(comparison['interpretation'])
print(f"P-value: {comparison['statistical_test']['p_value']:.4f}")
```

---

## Step 6: Generate Research Report

```python
from semantic_layer import GBDSemanticLayer

layer = GBDSemanticLayer()

# Get data for analysis
result = layer.ask_question(
    "Extract diabetes burden data for all countries, 2015-2023",
    categories=['causes', 'covariates']
)

df = parse_gemini_response(result['answer'])

# Generate comprehensive report
report = layer.generate_research_report(
    research_question="What is the global burden of diabetes and what are the projected trends?",
    data=df,
    analyses=['descriptive', 'temporal', 'forecast'],
    output_format='markdown'
)

# Save report
with open('diabetes_burden_report.md', 'w') as f:
    f.write(report)

print("✅ Report saved: diabetes_burden_report.md")
```

**Report includes:**
- Executive summary with citations
- Descriptive statistics
- Temporal trend analysis
- 5-year forecast
- Professional visualizations
- Citations to source CSV files

---

## Advanced Features

### Precise Metadata Filtering

```python
# Query only specific subsets
result = layer.ask_question(
    "How did cardiovascular deaths change from 2019 to 2023?",
    categories=['causes'],
    metadata_filter="year IN [2019, 2023] AND condition='Cardiovascular diseases' AND geography_level=global"
)
```

### Multi-Category Queries

```python
# Search across multiple categories
result = layer.ask_question(
    "What risk factors contribute most to diabetes burden?",
    categories=['causes', 'risks', 'covariates']  # Search all
)
```

### Extract Structured Data

```python
# Ask Gemini to return structured data
result = layer.ask_question(
    """
    Create a table of top 5 countries by diabetes prevalence in 2023.
    Columns: country, prevalence_per_100k, age_standardized_rate
    Format as CSV
    """,
    categories=['covariates']
)

# Parse directly into pandas
df = pd.read_csv(io.StringIO(result['answer']))
```

---

## Key Concepts

### 1. Vector Database Approach

```
Your CSV files are NOT loaded locally!
   ↓
They're stored in Gemini's vector database
   ↓
You query them via semantic search
   ↓
Get answers with citations
```

**Benefits:**
- Handle 250MB files (auto-split)
- Fast semantic search across 20GB
- No memory constraints
- Automatic citations

### 2. Filename = Metadata

```
IHME_GBD_2023_CAUSES_MORTALITY_GLOBAL_2023.csv
  ↓ Automatically extracts:
  • Organization: IHME
  • Year: 2023
  • Category: causes
  • Metric: mortality
  • Geography: global
```

**Use descriptive filenames!**

### 3. Grounded Analysis

```
Question → Vector DB (ground truth)
   ↓
Context + Citations
   ↓
Advanced Analytics (causal, forecast, A/B)
   ↓
Professional Report with Citations
```

Every answer is **grounded in your CSV data**.

---

## Costs

### One-Time Indexing
```
20GB data × 3 (embeddings) = 60GB storage used
~$750-$1,500 one-time indexing cost
Storage: FREE
```

### Ongoing Queries
```
Query embeddings: FREE
Gemini API usage: Standard pricing
  - gemini-2.5-flash: $0.075 / 1M tokens (recommended)
  - gemini-2.5-pro: $1.25 / 1M tokens
```

**Typical query costs: $0.01-$0.10 per question**

---

## Troubleshooting

### "Tier limit exceeded"
→ Upgrade to Tier 2 (100GB) or Tier 3 (1TB) at https://ai.google.dev/pricing

### "File too large"
→ Files >100MB are automatically split. No action needed!

### "No results found"
→ Check metadata filters. Try broader categories first.

### "Slow upload"
→ Normal for 20GB. Takes 30-60 minutes. Do this once!

---

## Next Steps

1. **Upload your data** (one-time, ~1 hour)
2. **Test semantic queries** (verify everything works)
3. **Run pilot analysis** (pick one research question)
4. **Generate first report** (with citations!)
5. **Scale to full research** (you're ready!)

---

## Example Research Questions You Can Answer

✅ "What are the trends in cardiovascular disease mortality from 1990-2023?"
✅ "How do diabetes outcomes differ between high and low-income countries?"
✅ "What will malaria burden be in 2030 based on current trends?"
✅ "Did COVID-19 lockdowns reduce traffic deaths significantly?"
✅ "Which risk factors contribute most to cancer DALYs globally?"
✅ "Compare mental health burden: USA vs India, 2019-2023"
✅ "What are the top 10 causes of death in children under 5?"

**All answered with citations to your original CSV files!**

---

## Resources

- **Full Guide:** `USAGE_GUIDE.md`
- **Example Scripts:** `examples/`
- **API Documentation:**
  - `gemini_file_search.py` - Vector DB interface
  - `advanced_analytics.py` - CausalImpact, Prophet, A/B testing
  - `semantic_layer.py` - Main research interface

---

## Support

Questions? Check the main README.md or review the example scripts in `examples/`.

**Ready to revolutionize your GBD research!** 🚀
