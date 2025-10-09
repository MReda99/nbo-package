# 📋 NBO Package - Complete End User Guide

## For Users Who Clone/Download the Repository

This guide shows exactly what end users need to do after getting your NBO package repository.

---

## 🚀 Step 1: Installation

### Prerequisites

- Python 3.8 or higher
- Git (if cloning) or download the repository as ZIP

### Get the Package

```bash
# Option A: Clone the repository
git clone <your-repository-url>
cd nbo-package

# Option B: Download ZIP and extract
# Download the ZIP file, extract it, and navigate to the folder
cd nbo-package
```

### Install the Package

```bash
# Install the package (this makes nbo-run commands available globally)
pip install -e .

# Verify installation
nbo-run --version
# Should output: nbo-package 1.0.0
```

**✅ After this step:** All `nbo-run` commands are available globally on their system.

---

## 📂 Step 2: Understand the Package Structure

```
nbo-package/
├── data/                          # ← Sample data (for reference only)
├── nbo/                           # ← Package code (don't modify)
│   ├── config/
│   │   ├── database_schema_v1.1.json  # ← YOUR SCHEMA (check this!)
│   │   └── settings.json               # ← Pipeline settings
│   └── [Python scripts]
├── output/                        # ← Results will go here
└── [Package files]
```

---

## 🔍 Step 3: Check the Schema Requirements

### View the Schema

```bash
# The schema file shows exactly what columns your CSV files need
# Location: nbo/config/database_schema_v1.1.json
```

**Or check it programmatically:**

```bash
# See what tables and columns are expected
nbo-run check-pipeline
```

### Create Data Templates (Recommended)

```bash
# This creates CSV templates with the exact schema requirements
nbo-run setup-data-templates --output-dir my_data

# This creates:
# my_data/
#   ├── offer_master.csv      (your offers/promotions)
#   ├── touch_history.csv     (customer communication history)
#   ├── feature_mart.csv      (customer features)
#   ├── modeling_set_v2.csv   (training data)
#   └── README.md            (detailed instructions)
```

---

## 📊 Step 4: Prepare Your Data

### Required Input Files

You need to provide these CSV files (use templates as reference):

1. **`offer_master.csv`** - Your promotion catalog

   - Required columns: `promotion_id`, `promotion_name`, `product_category`, `base_price`, `start_date`, `end_date`, `legal_flag`, `channel_eligibility`

2. **`touch_history.csv`** - Customer communication history

   - Required columns: `guest_id`, `promotion_id`, `touch_ts`, `channel`

3. **`feature_mart.csv`** - Customer features and transaction history

   - Required columns: `guest_id`, `asof_date`, `aov_28d`, `aov_90d`, `aov_365d`, etc. (37+ columns)

4. **`modeling_set_v2.csv`** - Training data (optional but recommended)
   - Required columns: `guest_id`, `response_within_window`, `treatment_flag`, `train_split`, etc.

### Where to Place Your Data

```bash
# Option A: Use the templates directory
# Edit the CSV files in my_data/ with your actual data

# Option B: Create your own data directory
mkdir user_data
# Copy your CSV files to user_data/
```

---

## ✅ Step 5: Validate Your Data

### Check Data Quality

```bash
# Validate your data against the schema
nbo-run --data-path my_data validate-user-data --save-report

# This will:
# ✓ Check all required columns exist
# ✓ Validate data types and formats
# ✓ Run business rule validations
# ✓ Generate quality scores
# ✓ Save detailed report as validation_report.json
```

### Validation Output

- ✅ **PASSED**: Data is ready for pipeline
- ⚠️ **PARTIAL**: Some files passed, some failed
- ❌ **FAILED**: Critical issues need fixing

---

## 🚀 Step 6: Run the Complete Pipeline

### Execute All Steps

```bash
# Run the complete NBO pipeline
nbo-run --data-path my_data --output-path results pipeline

# This executes all 7 steps in order:
# 1. catalog_guardrails    → processes your offer_master.csv
# 2. contract_checks       → validates offer catalog
# 3. fatigue_candidates    → generates candidates (needs feature_mart + touch_history)
# 4. model_training        → trains ML models and scores offers
# 5. guardrails_winners    → applies business rules and selects winners
# 6. test_marketing_view   → creates marketing campaign view
# 7. shap                  → adds model explanations
```

### Run Specific Steps (Optional)

```bash
# Run only certain steps
nbo-run --data-path my_data --output-path results pipeline --steps catalog_guardrails model_training

# Run individual step
nbo-run --data-path my_data --output-path results step model_training
```

---

## 📄 Step 7: Get Your Results

### Output Location

All results are saved in the `results/` directory (or whatever you specified with `--output-path`):

```
results/
├── model_scores_output.csv        # ← All scored guest-offer combinations
├── decision_log_output.csv        # ← Final offer decisions per customer
├── test_marketing_view_output.csv # ← Marketing campaign view
├── offer_catalog_v1.csv           # ← Processed offer catalog
└── scored_candidates.csv          # ← Candidates after fatigue filtering
```

### Key Output Files

1. **`model_scores_output.csv`** - Complete scoring results

   - Every guest-offer combination with ML scores
   - Columns: `guest_id`, `promotion_id`, `p_treat`, `p_ctrl`, `uplift`, `eim_raw`, etc.

2. **`decision_log_output.csv`** - Final decisions (ONE offer per customer)

   - The winning offer for each customer
   - Columns: `guest_id`, `promotion_id`, `eim_final`, `why_selected`, provenance fields

3. **`test_marketing_view_output.csv`** - Marketing-ready view
   - Combined view for campaign execution
   - Includes offer details, customer info, and decision rationale

---

## 🔧 Step 8: Troubleshooting & Help

### Common Commands

```bash
# Get help
nbo-run --help

# List all available pipeline steps
nbo-run list-steps

# Check if everything is configured correctly
nbo-run check-pipeline

# Validate just the data files (without schema)
nbo-run --data-path my_data validate-data
```

### Common Issues

**"Missing required files"**

```bash
# Use templates to see exactly what files you need
nbo-run setup-data-templates --output-dir templates
# Check templates/README.md for detailed requirements
```

**"Schema validation failed"**

```bash
# Check the schema file to see expected columns
# Location: nbo/config/database_schema_v1.1.json
# Or use templates to see the exact structure needed
```

**"Pipeline step failed"**

```bash
# Run steps individually to identify the problem
nbo-run --data-path my_data step catalog_guardrails
nbo-run --data-path my_data step model_training
```

---

## 📋 Complete Workflow Summary

```bash
# 1. Get the package
git clone <repo-url> && cd nbo-package

# 2. Install
pip install -e .

# 3. Create data templates
nbo-run setup-data-templates --output-dir my_data

# 4. Edit CSV files in my_data/ with your actual data

# 5. Validate your data
nbo-run --data-path my_data validate-user-data

# 6. Run the pipeline
nbo-run --data-path my_data --output-path results pipeline

# 7. Check results in results/ directory
```

**Total time:** ~10 minutes setup + data preparation time

**Result:** Professional NBO pipeline outputs with complete ML scoring and business rule optimization! 🎉

---

## 🎯 What You Get

- ✅ **Complete ML Pipeline**: Uplift modeling, scoring, optimization
- ✅ **Business Rules**: Fatigue management, margin floors, discount caps
- ✅ **Data Validation**: Against your JSON schema + business rules
- ✅ **Professional Outputs**: Ready for marketing campaign execution
- ✅ **Full Provenance**: Timestamps, versions, decision rationale
- ✅ **Quality Reports**: Data quality scores and validation details
