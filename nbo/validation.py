"""
Data validation utilities for the NBO package.

This module provides utilities for validating data quality and consistency.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataQualityReport:
    """Class to hold data quality assessment results."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.row_count = 0
        self.column_count = 0
        self.missing_data: Dict[str, float] = {}
        self.duplicate_rows = 0
        self.data_types: Dict[str, str] = {}
        self.numeric_stats: Dict[str, Dict[str, Any]] = {}
        self.categorical_stats: Dict[str, Dict[str, Any]] = {}
        self.issues: List[str] = []
        self.warnings: List[str] = []
    
    def add_issue(self, issue: str):
        """Add a data quality issue."""
        self.issues.append(issue)
        logger.warning(f"Data quality issue in {self.table_name}: {issue}")
    
    def add_warning(self, warning: str):
        """Add a data quality warning."""
        self.warnings.append(warning)
        logger.info(f"Data quality warning in {self.table_name}: {warning}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'table_name': self.table_name,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'missing_data': self.missing_data,
            'duplicate_rows': self.duplicate_rows,
            'data_types': self.data_types,
            'numeric_stats': self.numeric_stats,
            'categorical_stats': self.categorical_stats,
            'issues': self.issues,
            'warnings': self.warnings,
            'quality_score': self.calculate_quality_score()
        }
    
    def calculate_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)."""
        score = 100.0
        
        # Penalize for missing data
        avg_missing = np.mean(list(self.missing_data.values())) if self.missing_data else 0
        score -= avg_missing * 50  # Up to 50 points for missing data
        
        # Penalize for duplicate rows
        if self.row_count > 0:
            duplicate_rate = self.duplicate_rows / self.row_count
            score -= duplicate_rate * 30  # Up to 30 points for duplicates
        
        # Penalize for issues
        score -= len(self.issues) * 10  # 10 points per issue
        score -= len(self.warnings) * 2  # 2 points per warning
        
        return max(0.0, score)


def assess_data_quality(df: pd.DataFrame, table_name: str) -> DataQualityReport:
    """
    Assess data quality of a DataFrame.
    
    Args:
        df: DataFrame to assess
        table_name: Name of the table
        
    Returns:
        DataQualityReport with assessment results
    """
    report = DataQualityReport(table_name)
    
    # Basic statistics
    report.row_count = len(df)
    report.column_count = len(df.columns)
    
    if report.row_count == 0:
        report.add_issue("Table is empty")
        return report
    
    # Missing data analysis
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_rate = missing_count / len(df)
        report.missing_data[col] = missing_rate
        
        if missing_rate > 0.5:
            report.add_issue(f"Column '{col}' has {missing_rate:.1%} missing values")
        elif missing_rate > 0.2:
            report.add_warning(f"Column '{col}' has {missing_rate:.1%} missing values")
    
    # Duplicate rows
    report.duplicate_rows = df.duplicated().sum()
    if report.duplicate_rows > 0:
        duplicate_rate = report.duplicate_rows / len(df)
        if duplicate_rate > 0.1:
            report.add_issue(f"{report.duplicate_rows} duplicate rows ({duplicate_rate:.1%})")
        else:
            report.add_warning(f"{report.duplicate_rows} duplicate rows ({duplicate_rate:.1%})")
    
    # Data types
    for col in df.columns:
        report.data_types[col] = str(df[col].dtype)
    
    # Numeric column analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            stats = {
                'min': float(series.min()),
                'max': float(series.max()),
                'mean': float(series.mean()),
                'std': float(series.std()),
                'zeros': int((series == 0).sum()),
                'negatives': int((series < 0).sum())
            }
            report.numeric_stats[col] = stats
            
            # Check for suspicious patterns
            if stats['std'] == 0:
                report.add_warning(f"Column '{col}' has constant values")
            
            if stats['zeros'] / len(series) > 0.5:
                report.add_warning(f"Column '{col}' has {stats['zeros']/len(series):.1%} zero values")
    
    # Categorical column analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        series = df[col].dropna()
        if len(series) > 0:
            value_counts = series.value_counts()
            stats = {
                'unique_values': len(value_counts),
                'most_common': value_counts.head(5).to_dict(),
                'cardinality_ratio': len(value_counts) / len(series)
            }
            report.categorical_stats[col] = stats
            
            # Check for suspicious patterns
            if len(value_counts) == 1:
                report.add_warning(f"Column '{col}' has only one unique value")
            elif stats['cardinality_ratio'] > 0.95:
                report.add_warning(f"Column '{col}' has very high cardinality ({stats['cardinality_ratio']:.1%})")
    
    return report


def validate_business_rules(df: pd.DataFrame, table_name: str) -> List[str]:
    """
    Validate business-specific rules for NBO data.
    
    Args:
        df: DataFrame to validate
        table_name: Name of the table
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Common validations for NBO tables
    if 'guest_id' in df.columns:
        # Guest ID should not be null
        null_guests = df['guest_id'].isna().sum()
        if null_guests > 0:
            errors.append(f"Found {null_guests} rows with null guest_id")
        
        # Guest ID should be unique in decision tables
        if table_name in ['decision_log_v1', 'model_scores_v1']:
            duplicate_guests = df['guest_id'].duplicated().sum()
            if duplicate_guests > 0:
                errors.append(f"Found {duplicate_guests} duplicate guest_id values")
    
    if 'promotion_id' in df.columns:
        # Promotion ID should not be null
        null_promotions = df['promotion_id'].isna().sum()
        if null_promotions > 0:
            errors.append(f"Found {null_promotions} rows with null promotion_id")
    
    # Date validations
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_columns:
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col], errors='coerce')
            except:
                errors.append(f"Column '{col}' contains invalid date formats")
    
    # Probability validations
    prob_columns = [col for col in df.columns if col.startswith('p_') or 'prob' in col.lower()]
    for col in prob_columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            invalid_probs = ((df[col] < 0) | (df[col] > 1)).sum()
            if invalid_probs > 0:
                errors.append(f"Column '{col}' has {invalid_probs} values outside [0,1] range")
    
    # Margin validations
    margin_columns = [col for col in df.columns if 'margin' in col.lower()]
    for col in margin_columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            negative_margins = (df[col] < 0).sum()
            if negative_margins > 0:
                errors.append(f"Column '{col}' has {negative_margins} negative values")
    
    return errors


def check_data_consistency(dataframes: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
    """
    Check consistency across multiple related tables.
    
    Args:
        dataframes: Dictionary of table name to DataFrame
        
    Returns:
        Dictionary of table name to list of consistency issues
    """
    issues = {}
    
    # Check guest_id consistency
    guest_id_tables = {name: df for name, df in dataframes.items() if 'guest_id' in df.columns}
    
    if len(guest_id_tables) > 1:
        all_guest_ids = set()
        table_guest_ids = {}
        
        for table_name, df in guest_id_tables.items():
            table_guest_ids[table_name] = set(df['guest_id'].dropna().unique())
            all_guest_ids.update(table_guest_ids[table_name])
        
        # Check for guest IDs that appear in some tables but not others
        for table_name, guest_ids in table_guest_ids.items():
            missing_from_other_tables = []
            for other_table, other_guest_ids in table_guest_ids.items():
                if other_table != table_name:
                    missing = guest_ids - other_guest_ids
                    if missing:
                        missing_from_other_tables.append(f"{len(missing)} guest_ids not in {other_table}")
            
            if missing_from_other_tables:
                if table_name not in issues:
                    issues[table_name] = []
                issues[table_name].extend(missing_from_other_tables)
    
    # Check promotion_id consistency
    promotion_tables = {name: df for name, df in dataframes.items() if 'promotion_id' in df.columns}
    
    if 'offer_catalog_v1' in promotion_tables:
        catalog_promotions = set(promotion_tables['offer_catalog_v1']['promotion_id'].dropna().unique())
        
        for table_name, df in promotion_tables.items():
            if table_name != 'offer_catalog_v1':
                table_promotions = set(df['promotion_id'].dropna().unique())
                invalid_promotions = table_promotions - catalog_promotions
                
                if invalid_promotions:
                    if table_name not in issues:
                        issues[table_name] = []
                    issues[table_name].append(
                        f"{len(invalid_promotions)} promotion_ids not found in offer catalog"
                    )
    
    return issues
