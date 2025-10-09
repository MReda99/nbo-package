# 🚀 NBO Package - Quick Reference

## Essential Commands for End Users

### 1. Installation (One Time)

```bash
git clone <repository-url>
cd nbo-package
pip install -e .
```

### 2. Setup Data Templates

```bash
nbo-run setup-data-templates --output-dir my_data
```

**Result:** Creates CSV templates with exact schema requirements

### 3. Validate Your Data

```bash
nbo-run --data-path my_data validate-user-data --save-report
```

**Result:** Validates against JSON schema + generates quality report

### 4. Run Complete Pipeline

```bash
nbo-run --data-path my_data --output-path results pipeline
```

**Result:** Executes all 7 Python scripts, generates ML outputs

---

## Key Files & Locations

### Input Data (You Provide)

- `my_data/offer_master.csv` - Your promotions
- `my_data/touch_history.csv` - Communication history
- `my_data/feature_mart.csv` - Customer features
- `my_data/modeling_set_v2.csv` - Training data

### Schema Reference (Check Requirements)

- `nbo/config/database_schema_v1.1.json` - Exact column requirements

### Output Results (Generated)

- `results/model_scores_output.csv` - All ML scores
- `results/decision_log_output.csv` - Final decisions per customer
- `results/test_marketing_view_output.csv` - Marketing view

---

## Help Commands

```bash
nbo-run --help                    # General help
nbo-run list-steps                # See all pipeline steps
nbo-run check-pipeline            # Validate configuration
```

---

## Workflow: 4 Simple Steps

1. **Install** → `pip install -e .`
2. **Setup** → `nbo-run setup-data-templates --output-dir my_data`
3. **Edit** → Replace sample data with your actual data
4. **Run** → `nbo-run --data-path my_data --output-path results pipeline`

**Done!** Professional NBO results ready in `results/` directory.
