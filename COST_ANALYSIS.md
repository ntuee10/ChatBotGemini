# Precise Cost Analysis: GBD Semantic Layer (20GB Dataset)

This document provides detailed cost calculations for using Gemini File Search with your 20GB GBD 2023 dataset.

---

## 📊 Dataset Assumptions

Based on typical GBD 2023 data:

```
Total Size: 20 GB (20,480 MB)
File Count: ~50-200 CSV files (varies by category)
Row Count: ~100-500 million rows (across all files)
Columns per file: 10-30 columns (typical)
Data density: Mix of numeric, categorical, and text
```

**Example file structure:**
```csv
location_id,location_name,year,age_group,sex,cause_id,cause_name,deaths,dalys,ylds,ylls,rate_per_100k
123,United States,2023,50-54 years,Both,294,Diabetes mellitus,45678,1234567,567890,666677,42.5
...
```

---

## 💰 Gemini File Search Pricing (Official Rates)

### Indexing (One-Time)
- **Embedding generation at indexing time:** $0.15 per 1M tokens
- **Storage:** FREE (indefinitely)
- **Query-time embeddings:** FREE

### Query (Ongoing)
- **Retrieved document tokens:** Charged as regular context tokens
- **Gemini model usage:** Standard API pricing

**Source:** https://ai.google.dev/pricing (as of November 2025)

---

## 🔢 Token Count Estimation

### Method 1: Conservative Estimate (Text-Heavy Data)

CSV data with long text fields (location names, cause descriptions):

```
1 GB of CSV data ≈ 1,000 MB
1 MB of text ≈ 250,000 tokens (average)
20 GB = 20,000 MB
20,000 MB × 250,000 tokens/MB = 5,000,000,000 tokens (5 billion)
```

### Method 2: Aggressive Estimate (Numeric-Heavy Data)

CSV data mostly numeric (IDs, counts, rates):

```
1 MB of numeric CSV ≈ 350,000 tokens (numbers tokenize more efficiently)
20 GB = 20,000 MB
20,000 MB × 350,000 tokens/MB = 7,000,000,000 tokens (7 billion)
```

### Method 3: Realistic Estimate (Mixed GBD Data)

GBD files are typically 60% numeric, 40% text:

```
Numeric portion: 12 GB × 350,000 tokens/MB × 1,024 = 4,423,680,000 tokens
Text portion: 8 GB × 250,000 tokens/MB × 1,024 = 2,097,152,000 tokens
Total: ~6.5 billion tokens
```

**We'll use 6.5 billion tokens for our calculations.**

---

## 💵 One-Time Indexing Cost

### Calculation

```
Total tokens: 6,500,000,000 (6.5 billion)
Cost per 1M tokens: $0.15
Total indexing cost: (6,500,000,000 / 1,000,000) × $0.15
                   = 6,500 × $0.15
                   = $975
```

### Cost Range (Based on Different Estimates)

| Scenario | Token Count | Indexing Cost |
|----------|-------------|---------------|
| **Conservative** (text-heavy) | 5 billion | **$750** |
| **Realistic** (mixed GBD) | 6.5 billion | **$975** |
| **Aggressive** (numeric-heavy) | 7 billion | **$1,050** |

**Expected one-time cost: $975 ± $150**

### Important Notes

- ✅ This is a **ONE-TIME COST** - you never pay it again
- ✅ Storage is **FREE** forever
- ✅ You can delete and re-upload without penalty (if needed)
- ✅ Adding new files later: only pay for new files

---

## 📦 Storage Calculation

### Backend Storage Formula

```
Backend storage = Input data size × ~3 (embeddings overhead)
                = 20 GB × 3
                = 60 GB
```

### Storage Tier Requirements

| Tier | Storage Limit | Your Usage | Cost | Status |
|------|---------------|------------|------|--------|
| **Free** | 1 GB | 60 GB | Free | ❌ Insufficient |
| **Tier 1** | 10 GB | 60 GB | ? | ❌ Insufficient |
| **Tier 2** | 100 GB | 60 GB | ? | ✅ **Perfect fit** |
| **Tier 3** | 1 TB | 60 GB | ? | ✅ Plenty of room |

**You need Tier 2 (100 GB) minimum, or Tier 3 (1 TB) for future growth.**

**Current Tier 2 & 3 pricing:** Check https://ai.google.dev/gemini-api/docs/models/gemini (pricing varies by region)

---

## 🔍 Query Costs (Ongoing Usage)

### Cost Components

1. **Query embedding generation:** FREE
2. **Vector search:** FREE
3. **Retrieved document tokens:** Charged as input tokens to Gemini
4. **Gemini model response:** Standard API pricing

### Gemini Model Pricing (November 2025)

#### gemini-2.5-flash (Recommended for most queries)
```
Input:  $0.075 / 1M tokens  ($0.000000075 per token)
Output: $0.30 / 1M tokens   ($0.000000300 per token)
```

#### gemini-2.5-pro (For complex analysis)
```
Input:  $1.25 / 1M tokens   ($0.00000125 per token)
Output: $5.00 / 1M tokens   ($0.00000500 per token)
```

### Example Query Cost Breakdown

**Question:** "What were the top 10 causes of death globally in 2023?"

#### Scenario A: Simple Query (gemini-2.5-flash)

```
Query prompt: ~100 tokens
Retrieved context from File Search: ~2,000 tokens (relevant CSV chunks)
Total input: 2,100 tokens
Response: ~500 tokens

Cost calculation:
Input:  2,100 tokens × $0.000000075 = $0.0001575
Output:   500 tokens × $0.000000300 = $0.0001500
Total: $0.0003075 ≈ $0.0003 per query
```

**Cost: $0.0003 (less than 1/10th of a cent)**

#### Scenario B: Complex Analysis (gemini-2.5-pro)

```
Query prompt: ~200 tokens
Retrieved context: ~8,000 tokens (multiple CSV chunks + context)
Total input: 8,200 tokens
Response: ~2,000 tokens (detailed analysis)

Cost calculation:
Input:  8,200 tokens × $0.00000125 = $0.010250
Output: 2,000 tokens × $0.00000500 = $0.010000
Total: $0.020250 ≈ $0.02 per query
```

**Cost: $0.02 (2 cents per complex query)**

#### Scenario C: Research Report Generation (gemini-2.5-pro)

```
Query prompt: ~500 tokens (detailed report request)
Retrieved context: ~20,000 tokens (multiple files, comprehensive data)
Total input: 20,500 tokens
Response: ~5,000 tokens (executive summary + analysis)

Cost calculation:
Input:  20,500 tokens × $0.00000125 = $0.0256
Output:  5,000 tokens × $0.00000500 = $0.0250
Total: $0.0506 ≈ $0.05 per report
```

**Cost: $0.05 (5 cents per comprehensive report)**

---

## 📈 Monthly Usage Scenarios

### Light Usage (Individual Researcher)

**Profile:**
- 50 simple queries/month (Flash)
- 10 complex analyses/month (Pro)
- 2 research reports/month (Pro)

**Monthly cost:**
```
Simple queries:     50 × $0.0003  = $0.015
Complex analyses:   10 × $0.02    = $0.20
Research reports:    2 × $0.05    = $0.10
──────────────────────────────────────────
Total:                              $0.315 ≈ $0.32/month
```

**Annual cost: ~$3.80/year**

### Moderate Usage (Small Research Team)

**Profile:**
- 200 simple queries/month (Flash)
- 50 complex analyses/month (Pro)
- 10 research reports/month (Pro)

**Monthly cost:**
```
Simple queries:    200 × $0.0003  = $0.06
Complex analyses:   50 × $0.02    = $1.00
Research reports:   10 × $0.05    = $0.50
──────────────────────────────────────────
Total:                              $1.56/month
```

**Annual cost: ~$18.72/year**

### Heavy Usage (Large Research Lab)

**Profile:**
- 1,000 simple queries/month (Flash)
- 300 complex analyses/month (Pro)
- 50 research reports/month (Pro)
- 20 advanced forecasting runs/month (Pro, large context)

**Monthly cost:**
```
Simple queries:       1,000 × $0.0003  = $0.30
Complex analyses:       300 × $0.02    = $6.00
Research reports:        50 × $0.05    = $2.50
Advanced analytics:      20 × $0.15    = $3.00
──────────────────────────────────────────
Total:                                  $11.80/month
```

**Annual cost: ~$141.60/year**

### Enterprise Usage (Multi-Team Organization)

**Profile:**
- 5,000 queries/month (mixed Flash/Pro)
- 500 complex analyses/month
- 100 research reports/month
- Heavy automated analysis

**Monthly cost estimate: $50-100/month**
**Annual cost: $600-$1,200/year**

---

## 💡 Cost Optimization Strategies

### 1. Use gemini-2.5-flash for Most Queries

```
Flash vs Pro cost ratio: ~16x cheaper for input
Perfect for:
- Simple data retrieval
- Straightforward questions
- Quick lookups
- Exploratory queries

Use Pro only for:
- Complex causal analysis
- Multi-step reasoning
- Research report generation
- Publication-quality insights
```

**Savings: 80-90% by using Flash when appropriate**

### 2. Optimize Retrieved Context Size

```python
# Instead of retrieving all related data:
result = layer.ask_question(
    "Show me all diabetes data for all countries and years",  # ❌ Large context
    categories=['causes', 'risks', 'covariates']
)

# Be specific to reduce context size:
result = layer.ask_question(
    "What were diabetes deaths in USA in 2023?",  # ✅ Targeted
    categories=['causes'],
    year=2023,
    metadata_filter="country='United States'"
)
```

**Savings: 50-75% by using precise queries**

### 3. Cache Common Queries

```python
# For frequently asked questions, cache results locally
query_cache = {}

def cached_query(question, **kwargs):
    cache_key = hash((question, frozenset(kwargs.items())))
    if cache_key not in query_cache:
        query_cache[cache_key] = layer.ask_question(question, **kwargs)
    return query_cache[cache_key]
```

**Savings: 100% on repeated queries (free cache hits)**

### 4. Batch Extract Data Once, Analyze Locally

```python
# Extract data once via Gemini
result = layer.ask_question(
    "Extract diabetes prevalence data for all countries, 2015-2023, as CSV",
    categories=['covariates']
)

df = parse_gemini_response(result['answer'])  # One-time cost

# Now run multiple local analyses (free!)
forecast_usa = engine.prophet_forecast(df[df['country'] == 'USA'], ...)
forecast_india = engine.prophet_forecast(df[df['country'] == 'India'], ...)
forecast_china = engine.prophet_forecast(df[df['country'] == 'China'], ...)
# etc. - all free after initial extraction
```

**Savings: Extract once, analyze many times locally**

---

## 🎯 Total Cost of Ownership (3 Years)

### Scenario: Moderate Research Team

```
One-time indexing:                          $975
Year 1 queries (moderate usage):          × $18.72
Year 2 queries (moderate usage):          × $18.72
Year 3 queries (moderate usage):          × $18.72
─────────────────────────────────────────────────
Total 3-year cost:                        $1,031.16
Average per year:                            $343.72
Average per month:                            $28.64
```

### Cost Per Query (Amortized Over 3 Years)

```
Total queries over 3 years:
  200 simple/month × 36 months = 7,200 queries
   50 complex/month × 36 months = 1,800 queries
   10 reports/month × 36 months =   360 reports
Total: 9,360 operations

Average cost per operation: $1,031.16 / 9,360 = $0.11
```

**Average cost per query/analysis: $0.11 (11 cents)**

---

## 📊 Comparison with Alternatives

### Option 1: Gemini File Search (This Solution)

```
Setup: $975 one-time
Annual: $18.72/year (moderate usage)
Pros:
  ✅ Natural language queries
  ✅ Semantic search
  ✅ Citations to source
  ✅ No infrastructure management
  ✅ Scales to 1TB
Cons:
  ❌ Upfront indexing cost
```

### Option 2: Traditional Database (PostgreSQL + pgvector)

```
Setup: Free software, but:
  - Server costs: $50-200/month ($600-2,400/year)
  - ETL development: 40-80 hours @ $100/hr = $4,000-8,000
  - Maintenance: 5 hours/month @ $100/hr = $6,000/year

Total Year 1: $10,600-16,400
Total Year 3: $22,600-31,400
```

### Option 3: Elasticsearch + Custom RAG

```
Setup:
  - Elasticsearch cluster: $100-500/month ($1,200-6,000/year)
  - Development: 60-120 hours @ $100/hr = $6,000-12,000
  - OpenAI embeddings: $200-500/year
  - OpenAI queries: $300-600/year

Total Year 1: $7,700-19,100
Total Year 3: $9,300-26,300
```

### Option 4: Manual Analysis (Pandas + Jupyter)

```
Researcher time to answer questions:
  - Setup per analysis: 30-60 minutes
  - 10 analyses/month × 45 min avg = 7.5 hours/month
  - 7.5 hours/month × 12 months × $50/hr = $4,500/year

Total Year 1: $4,500
Total Year 3: $13,500

Cons:
  ❌ No semantic search
  ❌ Time-consuming
  ❌ Error-prone
  ❌ Not scalable
```

### Cost Comparison Summary (3 Years)

| Solution | Year 1 | Year 3 Total | Ongoing/Year |
|----------|--------|--------------|--------------|
| **Gemini File Search** | **$993.72** | **$1,031.16** | **~$19** |
| Traditional DB | $10,600 | $22,600 | ~$6,600 |
| Elasticsearch + RAG | $7,700 | $9,300 | ~$1,700 |
| Manual (Pandas) | $4,500 | $13,500 | ~$4,500 |

**Gemini File Search is 5-22x cheaper than alternatives over 3 years.**

---

## 🚨 Hidden Costs to Consider

### With Traditional Solutions

1. **Infrastructure management:** Server maintenance, updates, scaling
2. **Development time:** Building custom ETL, search, and analytics
3. **Debugging time:** Troubleshooting queries, optimizing performance
4. **Learning curve:** Training team on new systems
5. **Opportunity cost:** Time not spent on research

**Estimated hidden costs: $5,000-15,000/year**

### With Gemini File Search

1. **API key management:** Minimal (environment variable)
2. **Schema validation:** One-time setup (provided)
3. **Query optimization:** Learning best practices (days, not weeks)

**Estimated hidden costs: ~$500/year**

---

## 💰 Final Cost Summary

### One-Time Costs
```
Indexing 20GB of GBD data:           $975
Schema validation & prep:            $0 (provided scripts)
Initial setup & testing:             ~2-4 hours of your time
─────────────────────────────────────────
Total one-time:                      $975
```

### Ongoing Costs (Annual)

#### Light Usage
```
Individual researcher:               $3.80/year
```

#### Moderate Usage (Recommended)
```
Small research team:                 $18.72/year
```

#### Heavy Usage
```
Large research lab:                  $141.60/year
```

### Return on Investment (ROI)

**Time saved per query:**
- Manual analysis: 30-60 minutes
- Gemini semantic search: 30 seconds

**Value of time saved (moderate usage):**
```
260 queries/year × 45 min saved = 195 hours saved
195 hours × $50/hr = $9,750 value
Cost: $18.72
ROI: 520x return
```

**Every dollar spent saves ~$520 in researcher time.**

---

## 🎯 Recommendations

### For Your 20GB GBD Dataset

1. **Indexing budget:** Allocate **$975-1,050** for one-time upload
2. **Subscription tier:** Get **Tier 2 (100GB)** or **Tier 3 (1TB)**
3. **Query budget:** Plan for **$20-50/month** initially, adjust based on usage
4. **Use gemini-2.5-flash** for 80% of queries (16x cheaper)
5. **Cache common queries** to reduce redundant API calls

### Cost Control Best Practices

✅ Start with Flash model, upgrade to Pro only when needed
✅ Use specific metadata filters to reduce context size
✅ Cache frequently accessed data locally
✅ Extract data once, run multiple analyses locally
✅ Monitor usage with API dashboard

---

## 📞 Next Steps

1. **Verify your Gemini subscription tier** (need Tier 2+)
2. **Allocate ~$1,000 for indexing** (one-time)
3. **Start with light usage** to understand costs
4. **Scale based on actual usage patterns**

**The system is ready to use - all code is committed and documented!**

---

*Cost calculations based on Gemini API pricing as of November 2025. Prices subject to change. Check https://ai.google.dev/pricing for current rates.*
