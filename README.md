<div align="center">

[![Join AI Community](https://img.shields.io/badge/🚀_Join-AI_Community_(FREE)-4F46E5?style=for-the-badge)](https://www.skool.com/ai-for-your-business)
[![GitHub Profile](https://img.shields.io/badge/GitHub-@coffeefuelbump-181717?style=for-the-badge&logo=github)](https://github.com/coffeefuelbump)

[![Link Tree](https://img.shields.io/badge/Linktree-Everything-green?style=for-the-badge&logo=linktree&logoColor=white)](https://linktr.ee/corbin_brown)
[![YouTube Membership](https://img.shields.io/badge/YouTube-Become%20a%20Builder-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/channel/UCJFMlSxcvlZg5yZUYJT0Pug/join)

</div>

---

# 📊 CSV Data Summarizer + GBD Semantic Layer

A powerful Claude Skill that automatically analyzes CSV files and generates comprehensive insights with visualizations. Now enhanced with **Gemini File Search** for building a semantic layer over massive CSV datasets (20GB+) with advanced analytics.

## 🆕 NEW: GBD Semantic Layer (Research-Grade Analytics)

Transform your Global Burden of Disease (GBD) or any large CSV dataset into an intelligent, queryable system with:

- 🗃️ **Vector Database Storage** - Store 20GB+ of CSVs in Gemini File Search (up to 1TB)
- 🔍 **Semantic Search** - Ask questions in natural language, get cited answers from your data
- 📊 **Advanced Analytics** - CausalImpact, Prophet forecasting, A/B testing, temporal trends
- ✅ **Ground Truth Verification** - Schema validation + citations to source CSVs
- 📈 **Publication-Ready Reports** - Professional visualizations with statistical rigor

**Perfect for:** Epidemiological research, health economics, policy analysis, or any massive CSV dataset requiring semantic search + advanced analytics.

### Quick Start for GBD Semantic Layer

1. **Install:** `pip install -r requirements.txt`
2. **Upload CSVs:** 20GB of GBD data → Gemini File Search (one-time)
3. **Query:** Ask questions → Get answers with citations
4. **Analyze:** Run causal analysis, forecasting, A/B tests
5. **Report:** Generate publication-ready research reports

📚 **See:** [`QUICKSTART.md`](QUICKSTART.md) | [`USAGE_GUIDE.md`](USAGE_GUIDE.md) | [`SCHEMA_CONSISTENCY_GUIDE.md`](SCHEMA_CONSISTENCY_GUIDE.md)

---

## 🎯 Original Skill: CSV Data Summarizer

A powerful Claude Skill that automatically analyzes CSV files and generates comprehensive insights with visualizations. Upload any CSV and get instant, intelligent analysis without being asked what you want!

<div align="center">

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

</div>

## 🚀 Features

- **🤖 Intelligent & Adaptive** - Automatically detects data type (sales, customer, financial, survey, etc.) and applies relevant analysis
- **📈 Comprehensive Analysis** - Generates statistics, correlations, distributions, and trends
- **🎨 Auto Visualizations** - Creates multiple charts based on what's in your data:
  - Time-series plots for date-based data
  - Correlation heatmaps for numeric relationships
  - Distribution histograms
  - Categorical breakdowns
- **⚡ Proactive** - No questions asked! Just upload CSV and get complete analysis immediately
- **🔍 Data Quality Checks** - Automatically detects and reports missing values
- **📊 Multi-Industry Support** - Adapts to e-commerce, healthcare, finance, operations, surveys, and more

## 📥 Quick Download

<div align="center">

### Get Started in 2 Steps

**1️⃣ Download the Skill**  
[![Download Skill](https://img.shields.io/badge/Download-CSV%20Data%20Summarizer%20Skill-blue?style=for-the-badge&logo=download)](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill/raw/main/csv-data-summarizer.zip)

**2️⃣ Try the Demo Data**  
[![Download Demo CSV](https://img.shields.io/badge/Download-Sample%20P%26L%20Financial%20Data-green?style=for-the-badge&logo=data)](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill/raw/main/examples/showcase_financial_pl_data.csv)

</div>

---

## 📦 What's Included

### Original CSV Summarizer Skill
```
csv-data-summarizer-claude-skill/
├── SKILL.md              # Claude Skill definition
├── analyze.py            # Comprehensive analysis engine
├── examples/
│   └── showcase_financial_pl_data.csv  # Demo P&L financial dataset
└── resources/
    ├── sample.csv        # Example dataset
    └── README.md         # Usage documentation
```

### NEW: GBD Semantic Layer Components
```
├── gemini_file_search.py    # Gemini File Search integration & upload
├── advanced_analytics.py    # CausalImpact, Prophet, A/B testing, temporal trends
├── semantic_layer.py        # Main research interface (questions → insights)
├── gbd_schema_mapper.py     # Schema validation & column standardization
├── requirements.txt         # Updated dependencies (Gemini API, Prophet, etc.)
├── QUICKSTART.md            # 15-minute getting started guide
├── USAGE_GUIDE.md           # Complete usage documentation
├── SCHEMA_CONSISTENCY_GUIDE.md  # Ground truth integrity guide
└── examples/
    └── demo_filename_metadata.py  # Filename metadata extraction demo
```

## 🎯 How It Works

1. **Upload** any CSV file to Claude.ai
2. **Skill activates** automatically when CSV is detected
3. **Analysis runs** immediately - inspects data structure and adapts
4. **Results delivered** - Complete analysis with multiple visualizations

No prompting needed. No options to choose. Just instant, comprehensive insights!

## 📥 Installation

### For Claude.ai Users

1. Download the latest release: [`csv-data-summarizer.zip`](https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill/releases)
2. Go to [Claude.ai](https://claude.ai) → Settings → Capabilities → Skills
3. Upload the zip file
4. Enable the skill
5. Done! Upload any CSV and watch it work ✨

### For Developers

```bash
git clone git@github.com:coffeefuelbump/csv-data-summarizer-claude-skill.git
cd csv-data-summarizer-claude-skill
pip install -r requirements.txt
```

## 📊 Sample Dataset Highlights

The included demo CSV contains **15 months of P&L data** with:
- 3 product lines (SaaS, Enterprise, Services)
- 25 financial metrics including revenue, expenses, margins, CAC, LTV
- Quarterly trends showing business growth
- Perfect for showcasing time-series analysis, correlations, and financial insights

## 🎨 Example Use Cases

- **📊 Sales Data** → Revenue trends, product performance, regional analysis
- **👥 Customer Data** → Demographics, segmentation, geographic patterns
- **💰 Financial Data** → Transaction analysis, trend detection, correlations
- **⚙️ Operational Data** → Performance metrics, time-series analysis
- **📋 Survey Data** → Response distributions, cross-tabulations

## 🛠️ Technical Details

**Dependencies:**
- Python 3.8+
- pandas 2.0+
- matplotlib 3.7+
- seaborn 0.12+

**Visualizations Generated:**
- Time-series trend plots
- Correlation heatmaps
- Distribution histograms
- Categorical bar charts

## 📝 Example Output

```
============================================================
📊 DATA OVERVIEW
============================================================
Rows: 100 | Columns: 15

📋 DATA TYPES:
  • order_date: object
  • total_revenue: float64
  • customer_segment: object
  ...

🔍 DATA QUALITY:
✓ No missing values - dataset is complete!

📈 NUMERICAL ANALYSIS:
[Summary statistics for all numeric columns]

🔗 CORRELATIONS:
[Correlation matrix showing relationships]

📅 TIME SERIES ANALYSIS:
Date range: 2024-01-05 to 2024-04-11
Span: 97 days

📊 VISUALIZATIONS CREATED:
  ✓ correlation_heatmap.png
  ✓ time_series_analysis.png
  ✓ distributions.png
  ✓ categorical_distributions.png
```

## 🌟 Connect & Learn More

<div align="center">

[![Join AI Community](https://img.shields.io/badge/Join-AI%20Community%20(FREE)-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgM2MxLjY2IDAgMyAxLjM0IDMgM3MtMS4zNCAzLTMgMy0zLTEuMzQtMy0zIDEuMzQtMyAzLTN6bTAgMTQuMmMtMi41IDAtNC43MS0xLjI4LTYtMy4yMi4wMy0xLjk5IDQtMy4wOCA2LTMuMDggMS45OSAwIDUuOTcgMS4wOSA2IDMuMDgtMS4yOSAxLjk0LTMuNSAzLjIyLTYgMy4yMnoiLz48L3N2Zz4=)](https://www.skool.com/ai-for-your-business/about)

[![Link Tree](https://img.shields.io/badge/Linktree-Everything-green?style=for-the-badge&logo=linktree&logoColor=white)](https://linktr.ee/corbin_brown)

[![YouTube Membership](https://img.shields.io/badge/YouTube-Become%20a%20Builder-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/channel/UCJFMlSxcvlZg5yZUYJT0Pug/join)

[![Twitter Follow](https://img.shields.io/badge/Twitter-Follow%20@corbin__braun-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/corbin_braun)

</div>

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Share your use cases

## 📄 License

MIT License - feel free to use this skill for personal or commercial projects!

## 🙏 Acknowledgments

Built for the Claude Skills platform by [Anthropic](https://www.anthropic.com/news/skills).

---

<div align="center">

**Made with ❤️ for the AI community**

⭐ Star this repo if you find it useful!

</div>

