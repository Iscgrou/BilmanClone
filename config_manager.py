"""
Configuration Management for Bilman Deployment
Handles project configuration setup and management
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import configparser
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.supported_config_files = [
            "config.json",
            "config.yaml", 
            "config.yml",
            "config.ini",
            ".env",
            "settings.py",
            "app.config"
        ]

    def setup_config(self, project_dir: str, config_data: Dict[str, Any]) -> bool:
        """Setup project configuration with provided data"""
        try:
            logger.info("Setting up project configuration...")
            
            # Find existing config files
            existing_configs = self._find_config_files(project_dir)
            
            if existing_configs:
                # Update existing configuration files
                for config_file in existing_configs:
                    self._update_config_file(config_file, config_data)
            else:
                # Create new configuration file
                self._create_config_file(project_dir, config_data)
            
            # Create environment file for runtime
            self._create_env_file(project_dir, config_data)
            
            logger.info("Configuration setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration setup failed: {e}")
            return False

    def _find_config_files(self, project_dir: str) -> list:
        """Find existing configuration files in the project"""
        found_configs = []
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file in self.supported_config_files or file.endswith(('.config', '.conf')):
                    found_configs.append(os.path.join(root, file))
        
        logger.info(f"Found {len(found_configs)} configuration files")
        return found_configs

    def _update_config_file(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update an existing configuration file"""
        try:
            file_ext = Path(config_path).suffix.lower()
            filename = os.path.basename(config_path)
            
            logger.info(f"Updating configuration file: {config_path}")
            
            if filename.endswith('.json') or file_ext == '.json':
                return self._update_json_config(config_path, config_data)
            elif filename.endswith(('.yaml', '.yml')) or file_ext in ['.yaml', '.yml']:
                return self._update_yaml_config(config_path, config_data)
            elif filename.endswith('.ini') or file_ext == '.ini':
                return self._update_ini_config(config_path, config_data)
            elif filename == '.env' or filename.endswith('.env'):
                return self._update_env_config(config_path, config_data)
            elif filename.endswith('.py'):
                return self._update_python_config(config_path, config_data)
            else:
                # Try to handle as generic key-value pairs
                return self._update_generic_config(config_path, config_data)
                
        except Exception as e:
            logger.error(f"Failed to update config file {config_path}: {e}")
            return False

    def _update_json_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update JSON configuration file"""
        try:
            # Read existing config
            existing_config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
            
            # Merge configurations
            merged_config = {**existing_config, **config_data}
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(merged_config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update JSON config: {e}")
            return False

    def _update_yaml_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update YAML configuration file"""
        try:
            # Read existing config
            existing_config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    existing_config = yaml.safe_load(f) or {}
            
            # Merge configurations
            merged_config = {**existing_config, **config_data}
            
            # Write updated config
            with open(config_path, 'w') as f:
                yaml.dump(merged_config, f, default_flow_style=False)
            
            return True
        except ImportError:
            logger.warning("PyYAML not available, skipping YAML config update")
            return False
        except Exception as e:
            logger.error(f"Failed to update YAML config: {e}")
            return False

    def _update_ini_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update INI configuration file"""
        try:
            config = configparser.ConfigParser()
            
            # Read existing config
            if os.path.exists(config_path):
                config.read(config_path)
            
            # Add/update bilman section
            if not config.has_section('bilman'):
                config.add_section('bilman')
            
            for key, value in config_data.items():
                config.set('bilman', key, str(value))
            
            # Write updated config
            with open(config_path, 'w') as f:
                config.write(f)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update INI config: {e}")
            return False

    def _update_env_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update environment configuration file"""
        try:
            # Read existing environment variables
            existing_vars = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            existing_vars[key] = value
            
            # Add new configuration variables
            for key, value in config_data.items():
                env_key = f"BILMAN_{key.upper()}"
                existing_vars[env_key] = str(value)
            
            # Write updated environment file
            with open(config_path, 'w') as f:
                f.write("# Bilman Configuration\n")
                for key, value in existing_vars.items():
                    f.write(f"{key}={value}\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to update ENV config: {e}")
            return False

    def _update_python_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update Python configuration file"""
        try:
            # Read existing file content
            content = ""
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
            
            # Add bilman configuration section
            bilman_config = "\n# Bilman Configuration\n"
            for key, value in config_data.items():
                var_name = f"BILMAN_{key.upper()}"
                if isinstance(value, str):
                    bilman_config += f'{var_name} = "{value}"\n'
                else:
                    bilman_config += f'{var_name} = {value}\n'
            
            # Append configuration if not already present
            if "# Bilman Configuration" not in content:
                content += bilman_config
            
            # Write updated file
            with open(config_path, 'w') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update Python config: {e}")
            return False

    def _update_generic_config(self, config_path: str, config_data: Dict[str, Any]) -> bool:
        """Update generic configuration file"""
        try:
            # Read existing content
            content = ""
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
            
            # Add bilman configuration section
            bilman_section = "\n# Bilman Configuration\n"
            for key, value in config_data.items():
                bilman_section += f"bilman.{key}={value}\n"
            
            # Append if not already present
            if "# Bilman Configuration" not in content:
                content += bilman_section
            
            # Write updated file
            with open(config_path, 'w') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update generic config: {e}")
            return False

    def _create_config_file(self, project_dir: str, config_data: Dict[str, Any]) -> bool:
        """Create new configuration file"""
        try:
            config_path = os.path.join(project_dir, "bilman_config.json")
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Created new configuration file: {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create config file: {e}")
            return False

    def _create_env_file(self, project_dir: str, config_data: Dict[str, Any]) -> bool:
        """Create environment file for runtime configuration"""
        try:
            env_path = os.path.join(project_dir, ".bilman.env")
            
            with open(env_path, 'w') as f:
                f.write("# Bilman Runtime Configuration\n")
                for key, value in config_data.items():
                    env_key = f"BILMAN_{key.upper()}"
                    f.write(f"{env_key}={value}\n")
            
            logger.info(f"Created environment file: {env_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create environment file: {e}")
            return False

    def load_config(self, project_dir: str) -> Optional[Dict[str, Any]]:
        """Load configuration from project directory"""
        try:
            # Try to load from bilman-specific files first
            bilman_config_path = os.path.join(project_dir, "bilman_config.json")
            if os.path.exists(bilman_config_path):
                with open(bilman_config_path, 'r') as f:
                    return json.load(f)
            
            # Try to load from environment file
            env_path = os.path.join(project_dir, ".bilman.env")
            if os.path.exists(env_path):
                config = {}
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.startswith('BILMAN_'):
                                config_key = key[7:].lower()  # Remove BILMAN_ prefix
                                config[config_key] = value
                return config
            
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
