# NBO Package - Next Best Offer Optimization

A machine learning pipeline for personalized offer optimization that processes customer data, trains uplift models, and generates optimal offer recommendations.

## Overview

The NBO (Next Best Offer) package implements a complete pipeline for:

1. **Data Processing**: Load and validate customer transaction data, feature marts, and offer catalogs
2. **Model Training**: Train uplift models to predict customer response probabilities
3. **Candidate Generation**: Create offer candidates while respecting fatigue rules
4. **Optimization**: Apply guardrails and select optimal offers based on Expected Incremental Margin (EIM)
5. **Decision Output**: Generate final offer decisions with full provenance tracking

## Installation

### From Source

```bash
git clone https://github.com/your-org/nbo-package.git
cd nbo-package
pip install -e .
```

### For Development

```bash
git clone https://github.com/your-org/nbo-package.git
cd nbo-package
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from nbo import NBOPipeline, NBOConfig

# Load configuration
config = NBOConfig.from_file("config/database_schema_v1.1.json")

# Initialize pipeline
pipeline = NBOPipeline(
    data_path="data/",
    config=config,
    output_path="output/"
)

# Run the complete pipeline
results = pipeline.run()
```

### Command Line Interface

```bash
# Run the full pipeline
nbo-pipeline --data-path ./data --config-path ./config --output-path ./output

# Run individual components
nbo-run model-training --input feature_mart.csv --output model_scores.csv
nbo-run guardrails --input model_scores.csv --output decisions.csv
```

## Data Requirements

The package expects the following CSV files in your data directory:

### Core Tables

- `dbo.feature_mart.csv` - Customer features and transaction history
- `dbo.modeling_set_v2.csv` - Training data with treatment/control labels
- `dbo.offer_catalog_v1.csv` - Available offers and their properties

### Supporting Tables

- `dbo.stg_touch_history.csv` - Customer communication history for fatigue rules
- `dbo.guardrail_config.csv` - Business rules and constraints
- Additional tables as defined in your schema configuration

## Configuration

The package uses a JSON schema file to define expected data structure:

```json
{
    "database": "subway_nbo_v2",
    "schemas": {
        "dbo": {
            "tables": {
                "feature_mart": {
                    "columns": [
                        {"name": "guest_id", "data_type": "nvarchar"},
                        {"name": "asof_date", "data_type": "datetime2"},
                        ...
                    ]
                }
            }
        }
    }
}
```

## Pipeline Components

### 1. Data Loading (`DataLoader`)

- Validates CSV files against schema
- Handles missing files gracefully
- Converts data types appropriately

### 2. Model Training (`ModelTrainer`)

- Trains uplift models using gradient boosting
- Handles treatment/control group validation
- Generates probability scores and uplift estimates

### 3. Candidate Generation (`fatigue_candidates.py`)

- Creates guest-offer combinations
- Applies 72-hour fatigue rules
- Filters for active, legal offers

### 4. Guardrails (`guardrails_winners.py`)

- Enforces margin floors and discount caps
- Ranks offers by Expected Incremental Margin (EIM)
- Selects optimal offer per customer

## Output

The pipeline generates:

- `model_scores_output.parquet` - All scored guest-offer combinations
- `decision_log_output.parquet` - Final offer decisions per customer
- Provenance tracking with timestamps and model versions

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black nbo/
isort nbo/
```

### Type Checking

```bash
mypy nbo/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information about your problem
