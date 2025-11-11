# End User Workflow - Complete Example

> **Purpose**: This document demonstrates the complete end-user experience with concrete examples, showing exactly what users need to do and what they can expect from the NBO package.

This shows exactly what an end user needs to do to use your NBO package.

## Step-by-Step User Experience

### 1. Installation (One Command)

```bash
pip install nbo_package-1.0.0-py3-none-any.whl
```

### 2. Create Data Templates (One Command)

```bash
nbo-run setup-data-templates --output-dir my_company_data
```

**Result:** Creates 4 CSV templates with sample data and instructions:

- `my_company_data/offer_master.csv`
- `my_company_data/touch_history.csv`
- `my_company_data/feature_mart.csv`
- `my_company_data/modeling_set_v2.csv`
- `my_company_data/README.md`

### 3. Replace Sample Data

User edits the CSV files with their actual data (this is the only manual step)

### 4. Validate Data (One Command)

```bash
nbo-run --data-path my_company_data validate-user-data --save-report
```

**Result:**

- Validates all columns against your JSON schema
- Checks data quality and business rules
- Provides detailed quality scores
- Saves validation report

### 5. Run Pipeline (One Command)

```bash
nbo-run --data-path my_company_data --output-path results pipeline
```

**Result:** Generates all outputs:

- `results/decision_log_output.csv` - Final decisions
- `results/model_scores_output.csv` - All scores
- `results/test_marketing_view_output.csv` - Marketing view

## Total User Effort

- **Installation:** 30 seconds
- **Setup:** 2 minutes
- **Data preparation:** Variable (depends on their data)
- **Validation & execution:** 2 minutes
- **Total technical time:** ~5 minutes

## What Users DON'T Need To Do

- ❌ Install Python dependencies manually
- ❌ Understand the internal pipeline
- ❌ Write any code
- ❌ Configure anything
- ❌ Follow complex guides
- ❌ Understand schema structure (templates show them)

## What Users GET

- Professional NBO pipeline results
- Complete data validation
- Full provenance tracking
- Quality reports
- Ready-to-use marketing outputs
- Built-in help system

## Example User Commands

```bash
# Complete workflow in 4 commands:
pip install nbo_package-1.0.0-py3-none-any.whl
nbo-run setup-data-templates --output-dir my_data
# [User edits CSV files]
nbo-run --data-path my_data validate-user-data
nbo-run --data-path my_data --output-path results pipeline
```

## Support Commands

```bash
# Get help
nbo-run --help

# Check what pipeline will do
nbo-run list-steps

# Validate system setup
nbo-run check-pipeline

# Run individual steps if needed
nbo-run --data-path my_data step catalog_guardrails
```

This is as simple as it gets for end users while maintaining full validation against your JSON schema!
