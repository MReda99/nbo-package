"""
Data loading and validation utilities for the NBO package.

This module provides utilities to:
- Load CSV files from the data directory
- Validate data against schema configurations
- Handle data type conversions and preprocessing
- Manage file paths and data discovery
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from datetime import datetime
import warnings

from .configuration import NBOConfig, get_config

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Exception raised when data validation fails."""
    pass


class DataLoader:
    """Main data loader class for the NBO package."""
    
    def __init__(self, data_path: Union[str, Path], config: Optional[NBOConfig] = None):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to data directory containing CSV files
            config: Configuration instance (uses default if None)
        """
        self.data_path = Path(data_path)
        self.config = config or get_config()
        self._validate_data_path()
        
        # Cache for loaded data
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._file_mapping: Dict[str, Path] = {}
        
        # Discover available data files
        self._discover_data_files()
    
    def _validate_data_path(self):
        """Validate that data path exists and is accessible."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {self.data_path}")
        
        if not self.data_path.is_dir():
            raise ValueError(f"Data path is not a directory: {self.data_path}")
    
    def _discover_data_files(self):
        """Discover and map available CSV files."""
        csv_files = list(self.data_path.glob("*.csv"))
        
        for csv_file in csv_files:
            # Extract table name from filename
            # Handle formats like "dbo.table_name.csv" or "table_name.csv"
            filename = csv_file.stem
            
            # Remove schema prefix if present (e.g., "dbo.table_name" -> "table_name")
            if '.' in filename:
                parts = filename.split('.')
                if len(parts) >= 2:
                    table_name = '.'.join(parts[1:])  # Everything after first dot
                else:
                    table_name = filename
            else:
                table_name = filename
            
            self._file_mapping[table_name] = csv_file
            logger.debug(f"Discovered data file: {table_name} -> {csv_file}")
        
        logger.info(f"Discovered {len(self._file_mapping)} data files in {self.data_path}")
    
    def get_available_tables(self) -> List[str]:
        """Get list of available table names."""
        return list(self._file_mapping.keys())
    
    def load_table(self, table_name: str, validate_schema: bool = True, 
                   cache: bool = True, **kwargs) -> pd.DataFrame:
        """
        Load a table from CSV file.
        
        Args:
            table_name: Name of the table to load
            validate_schema: Whether to validate against schema configuration
            cache: Whether to cache the loaded data
            **kwargs: Additional arguments passed to pd.read_csv()
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If table file is not found
            DataValidationError: If schema validation fails
        """
        # Check cache first
        if cache and table_name in self._data_cache:
            logger.debug(f"Loading {table_name} from cache")
            return self._data_cache[table_name].copy()
        
        # Find the file
        if table_name not in self._file_mapping:
            raise FileNotFoundError(f"Table '{table_name}' not found. Available tables: {self.get_available_tables()}")
        
        file_path = self._file_mapping[table_name]
        logger.info(f"Loading table '{table_name}' from {file_path}")
        
        try:
            # Load CSV with default parameters
            default_kwargs = {
                'encoding': 'utf-8',
                'low_memory': False,
            }
            default_kwargs.update(kwargs)
            
            df = pd.read_csv(file_path, **default_kwargs)
            
            # Basic data cleaning
            df = self._clean_data(df, table_name)
            
            # Validate schema if requested
            if validate_schema:
                self._validate_schema(df, table_name)
            
            # Apply data type conversions
            df = self._apply_data_types(df, table_name)
            
            # Cache if requested
            if cache:
                self._data_cache[table_name] = df.copy()
            
            logger.info(f"Successfully loaded {table_name}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load table '{table_name}': {e}")
            raise
    
    def _clean_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Apply basic data cleaning operations.
        
        Args:
            df: Input DataFrame
            table_name: Name of the table
            
        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                # Convert 'nan' strings back to NaN
                df[col] = df[col].replace(['nan', 'None', ''], np.nan)
        
        return df
    
    def _validate_schema(self, df: pd.DataFrame, table_name: str):
        """
        Validate DataFrame against schema configuration.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table
            
        Raises:
            DataValidationError: If validation fails
        """
        if not self.config.database_config:
            logger.warning("No database configuration available for schema validation")
            return
        
        validation_result = self.config.validate_table_columns(table_name, df.columns.tolist())
        
        if validation_result['missing']:
            logger.warning(f"Missing columns in {table_name}: {validation_result['missing']}")
        
        if validation_result['extra']:
            logger.info(f"Extra columns in {table_name}: {validation_result['extra']}")
        
        # Only raise error for critical missing columns
        critical_missing = [col for col in validation_result['missing'] 
                          if not col.startswith('_') and col not in ['id', 'created_at', 'updated_at']]
        
        if critical_missing:
            raise DataValidationError(
                f"Critical columns missing in {table_name}: {critical_missing}"
            )
    
    def _apply_data_types(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Apply appropriate data types based on schema configuration.
        
        Args:
            df: Input DataFrame
            table_name: Name of the table
            
        Returns:
            DataFrame with converted data types
        """
        table_config = self.config.get_table_config(table_name)
        if not table_config:
            return self._infer_data_types(df)
        
        for column_config in table_config.columns:
            col_name = column_config.name
            
            if col_name not in df.columns:
                continue
            
            try:
                df[col_name] = self._convert_column_type(df[col_name], column_config.data_type)
            except Exception as e:
                logger.warning(f"Failed to convert column {col_name} to {column_config.data_type}: {e}")
        
        return df
    
    def _convert_column_type(self, series: pd.Series, data_type: str) -> pd.Series:
        """
        Convert a pandas Series to the specified data type.
        
        Args:
            series: Input Series
            data_type: Target data type
            
        Returns:
            Converted Series
        """
        data_type_lower = data_type.lower()
        
        if 'int' in data_type_lower:
            return pd.to_numeric(series, errors='coerce').astype('Int64')
        
        elif 'float' in data_type_lower or 'decimal' in data_type_lower:
            return pd.to_numeric(series, errors='coerce')
        
        elif 'datetime' in data_type_lower or 'timestamp' in data_type_lower:
            return pd.to_datetime(series, errors='coerce', utc=True)
        
        elif 'date' in data_type_lower:
            return pd.to_datetime(series, errors='coerce').dt.date
        
        elif 'bool' in data_type_lower or 'bit' in data_type_lower:
            # Handle various boolean representations
            bool_map = {'true': True, 'false': False, '1': True, '0': False, 
                       'yes': True, 'no': False, 'y': True, 'n': False}
            return series.astype(str).str.lower().map(bool_map).astype('boolean')
        
        else:
            # Default to string
            return series.astype(str)
    
    def _infer_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Infer appropriate data types when no schema is available.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with inferred data types
        """
        for col in df.columns:
            # Try to convert datetime columns
            if any(keyword in col.lower() for keyword in ['date', 'time', 'ts']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    continue
                except:
                    pass
            
            # Try to convert numeric columns
            if df[col].dtype == 'object':
                # Try integer first
                numeric = pd.to_numeric(df[col], errors='coerce')
                if not numeric.isna().all():
                    # Check if all non-null values are integers
                    if numeric.dropna().apply(lambda x: x.is_integer()).all():
                        df[col] = numeric.astype('Int64')
                    else:
                        df[col] = numeric
        
        return df
    
    def load_multiple_tables(self, table_names: List[str], **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Load multiple tables at once.
        
        Args:
            table_names: List of table names to load
            **kwargs: Arguments passed to load_table()
            
        Returns:
            Dictionary mapping table names to DataFrames
        """
        results = {}
        
        for table_name in table_names:
            try:
                results[table_name] = self.load_table(table_name, **kwargs)
            except Exception as e:
                logger.error(f"Failed to load table {table_name}: {e}")
                if kwargs.get('strict', False):
                    raise
        
        return results
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        if table_name not in self._file_mapping:
            raise FileNotFoundError(f"Table '{table_name}' not found")
        
        file_path = self._file_mapping[table_name]
        
        # Get basic file info
        stat = file_path.stat()
        info = {
            'table_name': table_name,
            'file_path': str(file_path),
            'file_size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
        }
        
        # Try to get row count and column info without loading full data
        try:
            # Read just the header and a few rows
            sample_df = pd.read_csv(file_path, nrows=5)
            info.update({
                'columns': sample_df.columns.tolist(),
                'column_count': len(sample_df.columns),
            })
            
            # Estimate row count (this is approximate)
            if stat.st_size > 0:
                bytes_per_row = stat.st_size / (len(sample_df) + 1)  # +1 for header
                estimated_rows = int(stat.st_size / bytes_per_row) - 1
                info['estimated_rows'] = estimated_rows
            
        except Exception as e:
            logger.warning(f"Could not read table info for {table_name}: {e}")
        
        return info
    
    def clear_cache(self):
        """Clear the data cache."""
        self._data_cache.clear()
        logger.info("Data cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data."""
        return {
            'cached_tables': list(self._data_cache.keys()),
            'cache_size': len(self._data_cache),
            'memory_usage': sum(df.memory_usage(deep=True).sum() for df in self._data_cache.values())
        }


# Convenience functions
def load_data(data_path: Union[str, Path], config: Optional[NBOConfig] = None) -> DataLoader:
    """
    Create a DataLoader instance.
    
    Args:
        data_path: Path to data directory
        config: Configuration instance
        
    Returns:
        DataLoader instance
    """
    return DataLoader(data_path, config)


def quick_load(table_name: str, data_path: Union[str, Path] = "data") -> pd.DataFrame:
    """
    Quickly load a single table with default settings.
    
    Args:
        table_name: Name of the table to load
        data_path: Path to data directory
        
    Returns:
        Loaded DataFrame
    """
    loader = DataLoader(data_path)
    return loader.load_table(table_name)
