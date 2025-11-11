# COMPLETE NBO Package Functionality

> **Purpose**: This document provides a comprehensive overview of the complete NBO package functionality, explaining both validation and execution capabilities to help stakeholders understand the full value proposition.

## What Your Package Actually Does (Both Validation AND Execution)

Your package provides **COMPLETE END-TO-END NBO PIPELINE**, not just validation:

### **1. Schema Validation** (Input Validation)

- Validates user CSV files against your `database_schema_v1.1.json`
- Checks column names, data types, business rules
- Provides data quality scores and reports

### **2. Complete Pipeline Execution** (Your Python Scripts)

- **Executes all 7 of your Python scripts** in correct dependency order
- **Generates all outputs** as specified in your workflow
- **Full workflow orchestration** with error handling

## Complete User Workflow

### Step 1: User Provides Data + Validation

```bash
# User creates their data
nbo-run setup-data-templates --output-dir my_data
# [User replaces sample data with their actual data]

# VALIDATES against your JSON schema
nbo-run --data-path my_data validate-user-data
```

### Step 2: EXECUTES Your Python Scripts + Generates Outputs

```bash
# RUNS ALL YOUR PYTHON SCRIPTS and generates outputs
nbo-run --data-path my_data --output-path results pipeline
```

This executes **your exact workflow**:

## **What Actually Runs (Your Python Scripts)**

1. **`catalog_guardrails.py`**

   - Input: User's offer catalog data
   - Output: `offer_catalog_v1.csv`

2. **`contract_checks.py`**

   - Input: `offer_catalog_v1.csv`
   - Output: `offer_catalog_v1.csv` (validated)

3. **`fatigue_candidates.py`**

   - Inputs: `feature_mart.csv`, `touch_history.csv`, `offer_catalog_v1.csv`
   - Output: `scored_candidates.csv`

4. **`model_training.py`**

   - Inputs: User's offer data, `scored_candidates.csv`, `offer_catalog_v1.csv`
   - Output: `model_scores_output.csv` ⭐

5. **`guardrails_winners.py`**

   - Input: `model_scores_output.csv`
   - Output: `decision_log_output.csv` ⭐

6. **`test_marketing_view.py`**

   - Inputs: `offer_catalog_v1.csv`, `decision_log_output.csv`
   - Output: `test_marketing_view_output.csv`

7. **`shap.py`**
   - Input: `decision_log_output.csv`
   - Output: `decision_log_output.csv` (enhanced)

## 📄 **Final Outputs Generated**

Users get **professional NBO results**:

### **Primary Outputs:**

- **`model_scores_output.csv`** - All scored guest-offer combinations
- **`decision_log_output.csv`** - Final offer decisions per customer

### **Additional Outputs:**

- **`test_marketing_view_output.csv`** - Marketing campaign view
- **`offer_catalog_v1.csv`** - Processed offer catalog
- **`scored_candidates.csv`** - Candidate offers after fatigue filtering

## **Complete Value Proposition**

### **For Users:**

1. **Easy Data Input** - Templates with your exact schema
2. **Automatic Validation** - Against your JSON schema + business rules
3. **Complete NBO Processing** - All your Python scripts executed
4. **Professional Outputs** - Ready-to-use marketing decisions
5. **Zero Technical Complexity** - Just provide data and run commands

### **For You:**

1. **Schema Control** - Your JSON enforces data structure
2. **Business Logic Control** - Your Python scripts run exactly as designed
3. **Quality Control** - Built-in validation and error handling
4. **Easy Distribution** - Single wheel file installation

## **User Experience Summary**

```bash
# 1. Install (30 seconds)
pip install nbo_package-1.0.0-py3-none-any.whl

# 2. Setup data templates (30 seconds)
nbo-run setup-data-templates --output-dir my_data

# 3. User edits CSV files with their data (variable time)

# 4. Validate data against your schema (30 seconds)
nbo-run --data-path my_data validate-user-data

# 5. RUN YOUR COMPLETE PIPELINE (2-10 minutes depending on data size)
nbo-run --data-path my_data --output-path results pipeline

# RESULT: Complete NBO outputs ready for business use!
```

## **What Users Get**

### **Input:** Their CSV files (validated against your schema)

### **Output:** Complete NBO pipeline results

- `results/model_scores_output.csv` - **Your model training script output**
- `results/decision_log_output.csv` - **Your guardrails script output**
- `results/test_marketing_view_output.csv` - **Marketing-ready view**
- Full provenance tracking and quality reports

**This is a COMPLETE NBO SOLUTION, not just validation!**

Your package takes user data, validates it, runs your entire ML pipeline, and produces professional NBO results.
