"""
Configuration management system for the NBO package.

This module provides utilities to:
- Load and validate database schema configurations
- Manage application settings and parameters
- Handle environment-specific configurations
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColumnConfig:
    """Configuration for a database column."""
    name: str
    data_type: str
    nullable: bool = True
    description: Optional[str] = None


@dataclass 
class TableConfig:
    """Configuration for a database table."""
    name: str
    columns: List[ColumnConfig] = field(default_factory=list)
    description: Optional[str] = None
    
    def get_column(self, column_name: str) -> Optional[ColumnConfig]:
        """Get column configuration by name."""
        for col in self.columns:
            if col.name == column_name:
                return col
        return None
    
    def get_column_names(self) -> List[str]:
        """Get list of all column names."""
        return [col.name for col in self.columns]


@dataclass
class SchemaConfig:
    """Configuration for a database schema."""
    name: str
    tables: Dict[str, TableConfig] = field(default_factory=dict)
    
    def get_table(self, table_name: str) -> Optional[TableConfig]:
        """Get table configuration by name."""
        return self.tables.get(table_name)


@dataclass
class DatabaseConfig:
    """Configuration for a database."""
    name: str
    schemas: Dict[str, SchemaConfig] = field(default_factory=dict)
    
    def get_schema(self, schema_name: str) -> Optional[SchemaConfig]:
        """Get schema configuration by name."""
        return self.schemas.get(schema_name)
    
    def get_table(self, schema_name: str, table_name: str) -> Optional[TableConfig]:
        """Get table configuration by schema and table name."""
        schema = self.get_schema(schema_name)
        if schema:
            return schema.get_table(table_name)
        return None


class NBOConfig:
    """Main configuration class for the NBO package."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file or directory
        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.database_config: Optional[DatabaseConfig] = None
        self.app_settings: Dict[str, Any] = {}
        self._load_configurations()
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration path."""
        # Look for config in package directory
        package_dir = Path(__file__).parent
        config_dir = package_dir / "config"
        
        if config_dir.exists():
            return config_dir
        
        # Fallback to current working directory
        return Path.cwd() / "config"
    
    def _load_configurations(self):
        """Load all configuration files."""
        try:
            self._load_database_schema()
            self._load_app_settings()
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_database_schema(self):
        """Load database schema configuration."""
        schema_files = list(self.config_path.glob("*schema*.json"))
        
        if not schema_files:
            logger.warning("No schema configuration files found")
            return
        
        # Use the first schema file found
        schema_file = schema_files[0]
        logger.info(f"Loading schema from {schema_file}")
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            self.database_config = self._parse_database_config(schema_data)
            
        except Exception as e:
            logger.error(f"Failed to load schema file {schema_file}: {e}")
            raise
    
    def _parse_database_config(self, schema_data: Dict[str, Any]) -> DatabaseConfig:
        """Parse database configuration from JSON data."""
        db_name = schema_data.get("database", "unknown")
        db_config = DatabaseConfig(name=db_name)
        
        schemas_data = schema_data.get("schemas", {})
        
        for schema_name, schema_info in schemas_data.items():
            schema_config = SchemaConfig(name=schema_name)
            
            tables_data = schema_info.get("tables", {})
            
            for table_name, table_info in tables_data.items():
                table_config = TableConfig(
                    name=table_name,
                    description=table_info.get("description")
                )
                
                columns_data = table_info.get("columns", [])
                
                for col_data in columns_data:
                    column_config = ColumnConfig(
                        name=col_data["name"],
                        data_type=col_data["data_type"],
                        nullable=col_data.get("nullable", True),
                        description=col_data.get("description")
                    )
                    table_config.columns.append(column_config)
                
                schema_config.tables[table_name] = table_config
            
            db_config.schemas[schema_name] = schema_config
        
        return db_config
    
    def _load_app_settings(self):
        """Load application settings."""
        settings_files = list(self.config_path.glob("*settings*.json"))
        
        for settings_file in settings_files:
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                self.app_settings.update(settings_data)
                logger.info(f"Loaded settings from {settings_file}")
                
            except Exception as e:
                logger.warning(f"Failed to load settings file {settings_file}: {e}")
    
    def get_table_config(self, table_name: str, schema_name: str = "dbo") -> Optional[TableConfig]:
        """
        Get table configuration.
        
        Args:
            table_name: Name of the table
            schema_name: Name of the schema (default: "dbo")
            
        Returns:
            TableConfig if found, None otherwise
        """
        if not self.database_config:
            return None
        
        return self.database_config.get_table(schema_name, table_name)
    
    def get_expected_columns(self, table_name: str, schema_name: str = "dbo") -> List[str]:
        """
        Get expected column names for a table.
        
        Args:
            table_name: Name of the table
            schema_name: Name of the schema (default: "dbo")
            
        Returns:
            List of column names
        """
        table_config = self.get_table_config(table_name, schema_name)
        if table_config:
            return table_config.get_column_names()
        return []
    
    def validate_table_columns(self, table_name: str, actual_columns: List[str], 
                             schema_name: str = "dbo") -> Dict[str, List[str]]:
        """
        Validate actual columns against expected schema.
        
        Args:
            table_name: Name of the table
            actual_columns: List of actual column names
            schema_name: Name of the schema (default: "dbo")
            
        Returns:
            Dictionary with 'missing' and 'extra' column lists
        """
        expected_columns = set(self.get_expected_columns(table_name, schema_name))
        actual_columns_set = set(actual_columns)
        
        return {
            'missing': list(expected_columns - actual_columns_set),
            'extra': list(actual_columns_set - expected_columns),
            'valid': len(expected_columns) > 0 and len(expected_columns - actual_columns_set) == 0
        }
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get application setting.
        
        Args:
            key: Setting key (supports dot notation like 'model.n_estimators')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.app_settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key: str, value: Any):
        """
        Set application setting.
        
        Args:
            key: Setting key (supports dot notation)
            value: Setting value
        """
        keys = key.split('.')
        current = self.app_settings
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "NBOConfig":
        """
        Create configuration from a specific file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            NBOConfig instance
        """
        config_path = Path(config_file)
        if config_path.is_file():
            config_path = config_path.parent
        
        return cls(config_path)
    
    def save_settings(self, output_file: Optional[Union[str, Path]] = None):
        """
        Save current settings to file.
        
        Args:
            output_file: Output file path (default: config/settings.json)
        """
        if output_file is None:
            output_file = self.config_path / "settings.json"
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.app_settings, f, indent=2)
        
        logger.info(f"Settings saved to {output_file}")


# Default configuration instance
_default_config: Optional[NBOConfig] = None


def get_config() -> NBOConfig:
    """Get the default configuration instance."""
    global _default_config
    if _default_config is None:
        _default_config = NBOConfig()
    return _default_config


def set_config(config: NBOConfig):
    """Set the default configuration instance."""
    global _default_config
    _default_config = config
