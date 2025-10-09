"""
User data setup and validation utilities for the NBO package.

This module provides utilities for users to set up their own data
and validate it against the expected schema.
"""

import shutil
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

from .configuration import NBOConfig
from .data_loader import DataLoader
from .validation import assess_data_quality, validate_business_rules

logger = logging.getLogger(__name__)


class UserDataSetup:
    """Helper class for users to set up and validate their own data."""
    
    def __init__(self, config: Optional[NBOConfig] = None):
        """Initialize user data setup."""
        self.config = config or NBOConfig()
    
    def create_data_template(self, output_dir: Path = Path("data_template")) -> Dict[str, str]:
        """
        Create data template directory with required CSV templates.
        
        Args:
            output_dir: Directory to create templates in
            
        Returns:
            Dictionary mapping table names to template file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        templates_created = {}
        
        # Required input files for the pipeline
        required_tables = {
            'offer_master': [
                'promotion_id', 'promotion_name', 'product_category', 'base_price',
                'start_date', 'end_date', 'legal_flag', 'channel_eligibility'
            ],
            'touch_history': [
                'guest_id', 'promotion_id', 'touch_ts', 'channel'
            ],
            'feature_mart': [
                'guest_id', 'asof_date', 'aov_28d', 'aov_90d', 'aov_365d',
                'visit_frequency', 'days_since_last_visit'
            ],
            'modeling_set_v2': [
                'guest_id', 'response_within_window', 'treatment_flag', 
                'train_split', 'fold_id', 'code_commit_sha'
            ]
        }
        
        for table_name, required_columns in required_tables.items():
            # Get expected columns from schema if available
            expected_columns = self.config.get_expected_columns(table_name)
            
            # Use schema columns if available, otherwise use required columns
            columns = expected_columns if expected_columns else required_columns
            
            # Create empty CSV template
            template_df = pd.DataFrame(columns=columns)
            
            # Add one sample row with placeholder data
            sample_row = {}
            for col in columns:
                if 'id' in col.lower():
                    sample_row[col] = 'SAMPLE_ID_123'
                elif 'date' in col.lower() or 'time' in col.lower():
                    sample_row[col] = '2025-01-01'
                elif 'flag' in col.lower():
                    sample_row[col] = True
                elif 'price' in col.lower() or 'aov' in col.lower():
                    sample_row[col] = 10.50
                elif col.lower() in ['treatment_flag', 'response_within_window']:
                    sample_row[col] = 1
                else:
                    sample_row[col] = f'SAMPLE_{col.upper()}'
            
            template_df.loc[0] = sample_row
            
            # Save template
            template_file = output_dir / f"{table_name}.csv"
            template_df.to_csv(template_file, index=False)
            templates_created[table_name] = str(template_file)
            
            logger.info(f"Created template: {template_file}")
        
        # Create README for templates
        readme_content = self._create_template_readme(required_tables)
        readme_file = output_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Created {len(templates_created)} data templates in {output_dir}")
        return templates_created
    
    def _create_template_readme(self, required_tables: Dict[str, List[str]]) -> str:
        """Create README content for data templates."""
        content = """# NBO Data Templates

This directory contains CSV templates for the required input data files.

## Required Files

Replace the sample data in each file with your actual data:

"""
        
        for table_name, columns in required_tables.items():
            content += f"### {table_name}.csv\n"
            content += f"**Required columns:** {', '.join(columns)}\n"
            content += f"**Description:** "
            
            if table_name == 'offer_master':
                content += "Master catalog of all available offers/promotions\n"
            elif table_name == 'touch_history':
                content += "History of customer communications for fatigue management\n"
            elif table_name == 'feature_mart':
                content += "Customer features and transaction history\n"
            elif table_name == 'modeling_set_v2':
                content += "Training data with treatment/control labels\n"
            
            content += "\n"
        
        content += """
## Data Validation

After replacing the sample data with your actual data, run:

```bash
nbo-run validate-user-data --data-path ./data_template
```

This will validate your data against the expected schema and business rules.

## Next Steps

1. Replace sample data with your actual data
2. Validate the data using the command above
3. Copy validated files to your main data directory
4. Run the NBO pipeline: `nbo-run pipeline --data-path ./data_template`
"""
        
        return content
    
    def validate_user_data(self, data_path: Path, 
                          strict: bool = True) -> Dict[str, Any]:
        """
        Validate user-provided data against schema and business rules.
        
        Args:
            data_path: Path to user data directory
            strict: Whether to fail on validation errors
            
        Returns:
            Validation report dictionary
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {data_path}")
        
        logger.info(f"Validating user data in {data_path}")
        
        # Initialize data loader
        loader = DataLoader(data_path, self.config)
        available_tables = loader.get_available_tables()
        
        validation_report = {
            'data_path': str(data_path),
            'total_files': len(available_tables),
            'files_validated': 0,
            'files_passed': 0,
            'files_failed': 0,
            'validation_results': {},
            'overall_status': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        # Required files for pipeline
        required_files = ['offer_master', 'touch_history', 'feature_mart']
        
        # Check required files exist
        missing_required = [f for f in required_files if f not in available_tables]
        if missing_required:
            error_msg = f"Missing required files: {missing_required}"
            validation_report['errors'].append(error_msg)
            if strict:
                raise ValueError(error_msg)
        
        # Validate each available file
        for table_name in available_tables:
            validation_report['files_validated'] += 1
            
            try:
                # Load and validate data
                df = loader.load_table(table_name, validate_schema=True)
                
                # Data quality assessment
                quality_report = assess_data_quality(df, table_name)
                
                # Business rules validation
                business_errors = validate_business_rules(df, table_name)
                
                # Compile results
                file_result = {
                    'file_name': table_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'quality_score': quality_report.calculate_quality_score(),
                    'quality_issues': quality_report.issues,
                    'quality_warnings': quality_report.warnings,
                    'business_errors': business_errors,
                    'status': 'passed' if not business_errors and quality_report.calculate_quality_score() > 70 else 'failed'
                }
                
                validation_report['validation_results'][table_name] = file_result
                
                if file_result['status'] == 'passed':
                    validation_report['files_passed'] += 1
                    logger.info(f"✓ {table_name}: Validation passed")
                else:
                    validation_report['files_failed'] += 1
                    logger.warning(f"✗ {table_name}: Validation failed")
                    
                    # Add errors to main report
                    for error in business_errors:
                        validation_report['errors'].append(f"{table_name}: {error}")
                    
                    for issue in quality_report.issues:
                        validation_report['errors'].append(f"{table_name}: {issue}")
                
                # Add warnings
                for warning in quality_report.warnings:
                    validation_report['warnings'].append(f"{table_name}: {warning}")
                
            except Exception as e:
                validation_report['files_failed'] += 1
                error_msg = f"Failed to validate {table_name}: {str(e)}"
                validation_report['errors'].append(error_msg)
                logger.error(error_msg)
                
                if strict:
                    raise
        
        # Determine overall status
        if validation_report['files_failed'] == 0:
            validation_report['overall_status'] = 'passed'
        elif validation_report['files_passed'] > 0:
            validation_report['overall_status'] = 'partial'
        else:
            validation_report['overall_status'] = 'failed'
        
        logger.info(f"Validation complete: {validation_report['overall_status']}")
        logger.info(f"Files passed: {validation_report['files_passed']}/{validation_report['files_validated']}")
        
        return validation_report
    
    def copy_validated_data(self, source_path: Path, target_path: Path,
                          validation_report: Optional[Dict] = None) -> List[str]:
        """
        Copy validated data files to target directory.
        
        Args:
            source_path: Source data directory
            target_path: Target data directory
            validation_report: Previous validation report (optional)
            
        Returns:
            List of copied files
        """
        source_path = Path(source_path)
        target_path = Path(target_path)
        
        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)
        
        # If validation report provided, only copy passed files
        if validation_report:
            files_to_copy = [
                name for name, result in validation_report['validation_results'].items()
                if result['status'] == 'passed'
            ]
        else:
            # Copy all CSV files
            files_to_copy = [f.stem for f in source_path.glob("*.csv")]
        
        copied_files = []
        
        for file_name in files_to_copy:
            source_file = source_path / f"{file_name}.csv"
            target_file = target_path / f"{file_name}.csv"
            
            if source_file.exists():
                shutil.copy2(source_file, target_file)
                copied_files.append(str(target_file))
                logger.info(f"Copied {source_file} -> {target_file}")
        
        logger.info(f"Copied {len(copied_files)} validated files to {target_path}")
        return copied_files


def setup_user_data(output_dir: str = "data_template") -> Dict[str, str]:
    """
    Convenience function to create data templates.
    
    Args:
        output_dir: Directory to create templates in
        
    Returns:
        Dictionary mapping table names to template file paths
    """
    setup = UserDataSetup()
    return setup.create_data_template(Path(output_dir))


def validate_user_data(data_path: str, strict: bool = True) -> Dict[str, Any]:
    """
    Convenience function to validate user data.
    
    Args:
        data_path: Path to user data directory
        strict: Whether to fail on validation errors
        
    Returns:
        Validation report dictionary
    """
    setup = UserDataSetup()
    return setup.validate_user_data(Path(data_path), strict)
