# NBO Package - Installation & Usage Guide

> **Purpose**: This guide provides detailed installation and usage instructions for both end users (data scientists/analysts) and developers, including Python API examples and troubleshooting.

## 🚀 Quick Start

### Installation

```bash
# Install in development mode
cd nbo-package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check package is installed
python -c "import nbo; print(f'NBO Package v{nbo.__version__} installed successfully!')"

# Check CLI is available
nbo-run --help
```

## 📊 For End Users (Data Scientists/Analysts)

### Step 1: Set Up Your Data

```bash
# Create data templates
nbo-run setup-data-templates --output-dir my_data

# This creates:
# my_data/
#   ├── offer_master.csv      (your offers/promotions)
#   ├── touch_history.csv     (customer communication history)
#   ├── feature_mart.csv      (customer features)
#   ├── modeling_set_v2.csv   (training data)
#   └── README.md            (instructions)
```

### Step 2: Replace Sample Data

Edit the CSV files in `my_data/` with your actual data:

- **offer_master.csv**: Your promotion catalog
- **touch_history.csv**: Customer communication history
- **feature_mart.csv**: Customer transaction features
- **modeling_set_v2.csv**: Training data with treatment/control labels

### Step 3: Validate Your Data

```bash
# Validate data against schema
nbo-run --data-path my_data validate-user-data --save-report

# This will:
# ✓ Check required columns exist
# ✓ Validate data types and formats
# ✓ Run business rule validations
# ✓ Generate quality scores
# ✓ Save detailed report
```

### Step 4: Run the Pipeline

```bash
# Run complete NBO pipeline
nbo-run --data-path my_data --output-path results pipeline

# Or run specific steps
nbo-run --data-path my_data pipeline --steps catalog_guardrails model_training
```

### Step 5: View Results

Results will be in the `results/` directory:

- `decision_log_output.csv` - Final offer decisions per customer
- `model_scores_output.csv` - All scored guest-offer combinations
- `test_marketing_view_output.csv` - Marketing campaign view

## 🔧 For Developers

### Python API

```python
from nbo import NBOPipeline, setup_user_data, validate_user_data

# Set up user data templates
templates = setup_user_data("user_data")

# Validate user data
report = validate_user_data("user_data")

# Run pipeline programmatically
pipeline = NBOPipeline(data_path="user_data", output_path="results")
run_result = pipeline.run_pipeline()

print(f"Pipeline completed: {run_result.status}")
print(f"Steps completed: {len(run_result.steps_completed)}")
```

### Configuration

```python
from nbo import NBOConfig

# Load configuration
config = NBOConfig()

# Get/set model parameters
n_estimators = config.get_setting('model.n_estimators', 100)
config.set_setting('model.random_state', 42)

# Validate data against schema
expected_columns = config.get_expected_columns('feature_mart')
validation = config.validate_table_columns('feature_mart', actual_columns)
```

## 📋 Available Commands

```bash
# Data setup and validation
nbo-run setup-data-templates     # Create CSV templates
nbo-run validate-user-data       # Validate user data
nbo-run validate-data            # Validate existing data files

# Pipeline execution
nbo-run pipeline                 # Run complete pipeline
nbo-run step <step_name>         # Run single step
nbo-run list-steps              # List all available steps

# System checks
nbo-run check-pipeline          # Validate pipeline configuration
```

## 🔍 Troubleshooting

### Common Issues

1. **"Missing required files"**

   ```bash
   # Make sure you have the required input files
   nbo-run --data-path my_data validate-user-data
   ```

2. **"Schema validation failed"**

   ```bash
   # Check your CSV column names match expected schema
   # Use setup-data-templates to see required columns
   ```

3. **"Pipeline step failed"**
   ```bash
   # Run individual steps to isolate the issue
   nbo-run --data-path my_data step catalog_guardrails
   ```

### Getting Help

```bash
# General help
nbo-run --help

# Command-specific help
nbo-run pipeline --help
nbo-run validate-user-data --help
```

## 📁 File Structure

```
nbo-package/
├── nbo/                    # Main package
│   ├── __init__.py
│   ├── pipeline.py         # Workflow orchestration
│   ├── data_loader.py      # Data loading utilities
│   ├── configuration.py    # Configuration management
│   ├── user_setup.py       # User data setup utilities
│   ├── validation.py       # Data validation
│   ├── cli.py             # Command-line interface
│   ├── povenance.py        # Provenance tracking (Note: filename has typo, should be provenance.py)
│   └── config/            # Configuration files
├── data/                  # Sample data (for reference)
├── tests/                 # Test suite
├── setup.py              # Package setup
├── pyproject.toml        # Modern package configuration
└── README.md             # Documentation
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=nbo --cov-report=html

# Run basic functionality test
python tests/test_basic.py
```

## 🔄 Development Workflow

1. **Make changes** to the package code
2. **Run tests** to ensure nothing breaks
3. **Test CLI commands** with sample data
4. **Update version** in `nbo/_version.py`
5. **Build package** with `pip install -e .`

## 📦 Distribution

```bash
# Build distribution packages
python -m build

# Install from wheel
pip install dist/nbo_package-1.0.0-py3-none-any.whl
```
