"""
Project Analysis Module for Bilman Deployment
Analyzes project structure, dependencies, and potential issues
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
import subprocess

logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    def __init__(self):
        self.analysis_result = {}
        
    def analyze(self, project_dir: str) -> Dict[str, Any]:
        """Perform comprehensive project analysis"""
        logger.info(f"Starting analysis of project: {project_dir}")
        
        if not os.path.exists(project_dir):
            logger.error(f"Project directory not found: {project_dir}")
            return {}
        
        self.analysis_result = {
            "project_path": project_dir,
            "project_type": self._detect_project_type(project_dir),
            "structure": self._analyze_structure(project_dir),
            "dependencies": self._analyze_dependencies(project_dir),
            "configuration": self._analyze_configuration(project_dir),
            "potential_issues": self._identify_potential_issues(project_dir),
            "recommendations": []
        }
        
        # Generate recommendations based on analysis
        self._generate_recommendations()
        
        logger.info("Project analysis completed")
        return self.analysis_result
    
    def _detect_project_type(self, project_dir: str) -> Dict[str, Any]:
        """Detect the type of project (Node.js, Python, etc.)"""
        project_type = {
            "primary": "unknown",
            "technologies": [],
            "frameworks": []
        }
        
        # Check for Node.js project
        if os.path.exists(os.path.join(project_dir, "package.json")):
            project_type["primary"] = "nodejs"
            project_type["technologies"].append("javascript")
            
            # Analyze package.json for frameworks
            try:
                with open(os.path.join(project_dir, "package.json"), 'r') as f:
                    package_data = json.load(f)
                    dependencies = {**package_data.get("dependencies", {}), 
                                  **package_data.get("devDependencies", {})}
                    
                    # Detect common frameworks
                    if "express" in dependencies:
                        project_type["frameworks"].append("express")
                    if "react" in dependencies:
                        project_type["frameworks"].append("react")
                    if "vue" in dependencies:
                        project_type["frameworks"].append("vue")
                    if "angular" in dependencies:
                        project_type["frameworks"].append("angular")
                    if "next" in dependencies or "nextjs" in dependencies:
                        project_type["frameworks"].append("nextjs")
                        
            except Exception as e:
                logger.warning(f"Failed to parse package.json: {e}")
        
        # Check for Python project
        if (os.path.exists(os.path.join(project_dir, "requirements.txt")) or
            os.path.exists(os.path.join(project_dir, "setup.py")) or
            os.path.exists(os.path.join(project_dir, "pyproject.toml"))):
            
            if project_type["primary"] == "unknown":
                project_type["primary"] = "python"
            project_type["technologies"].append("python")
            
            # Check for Python frameworks
            if os.path.exists(os.path.join(project_dir, "requirements.txt")):
                try:
                    with open(os.path.join(project_dir, "requirements.txt"), 'r') as f:
                        requirements = f.read().lower()
                        if "django" in requirements:
                            project_type["frameworks"].append("django")
                        if "flask" in requirements:
                            project_type["frameworks"].append("flask")
                        if "fastapi" in requirements:
                            project_type["frameworks"].append("fastapi")
                        if "streamlit" in requirements:
                            project_type["frameworks"].append("streamlit")
                            
                except Exception as e:
                    logger.warning(f"Failed to parse requirements.txt: {e}")
        
        # Check for PHP project
        if (os.path.exists(os.path.join(project_dir, "composer.json")) or
            any(f.endswith('.php') for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f)))):
            if project_type["primary"] == "unknown":
                project_type["primary"] = "php"
            project_type["technologies"].append("php")
        
        # Check for Go project
        if (os.path.exists(os.path.join(project_dir, "go.mod")) or
            os.path.exists(os.path.join(project_dir, "go.sum"))):
            if project_type["primary"] == "unknown":
                project_type["primary"] = "go"
            project_type["technologies"].append("go")
        
        # Check for Ruby project
        if os.path.exists(os.path.join(project_dir, "Gemfile")):
            if project_type["primary"] == "unknown":
                project_type["primary"] = "ruby"
            project_type["technologies"].append("ruby")
        
        # Check for static site
        if any(f.endswith('.html') for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))):
            if project_type["primary"] == "unknown":
                project_type["primary"] = "static"
            project_type["technologies"].append("html")
        
        logger.info(f"Detected project type: {project_type}")
        return project_type
    
    def _analyze_structure(self, project_dir: str) -> Dict[str, Any]:
        """Analyze project directory structure"""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "important_files": [],
            "directories": []
        }
        
        important_files = [
            "README.md", "readme.md", "README.txt",
            "package.json", "requirements.txt", "setup.py",
            "Dockerfile", "docker-compose.yml",
            "Makefile", "makefile",
            ".env", ".env.example",
            "config.json", "config.yml", "config.yaml",
            "app.py", "main.py", "index.js", "server.js",
            "index.html", "index.php"
        ]
        
        for root, dirs, files in os.walk(project_dir):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'vendor']]
            
            structure["total_directories"] += len(dirs)
            
            for file in files:
                if file.startswith('.') and file not in ['.env', '.env.example']:
                    continue
                    
                structure["total_files"] += 1
                
                # Count file types
                ext = Path(file).suffix.lower()
                if ext:
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                
                # Check for important files
                if file in important_files:
                    structure["important_files"].append(os.path.relpath(os.path.join(root, file), project_dir))
            
            # Add directory to structure
            if root != project_dir:
                rel_dir = os.path.relpath(root, project_dir)
                structure["directories"].append(rel_dir)
        
        logger.info(f"Project structure: {structure['total_files']} files, {structure['total_directories']} directories")
        return structure
    
    def _analyze_dependencies(self, project_dir: str) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {
            "nodejs": {},
            "python": {},
            "system": [],
            "issues": []
        }
        
        # Analyze Node.js dependencies
        package_json_path = os.path.join(project_dir, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    dependencies["nodejs"] = {
                        "dependencies": package_data.get("dependencies", {}),
                        "devDependencies": package_data.get("devDependencies", {}),
                        "scripts": package_data.get("scripts", {})
                    }
            except Exception as e:
                dependencies["issues"].append(f"Failed to parse package.json: {e}")
        
        # Analyze Python dependencies
        requirements_path = os.path.join(project_dir, "requirements.txt")
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    requirements = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            requirements.append(line)
                    dependencies["python"]["requirements"] = requirements
            except Exception as e:
                dependencies["issues"].append(f"Failed to parse requirements.txt: {e}")
        
        # Check for system dependencies
        if os.path.exists(os.path.join(project_dir, "Dockerfile")):
            try:
                with open(os.path.join(project_dir, "Dockerfile"), 'r') as f:
                    dockerfile_content = f.read()
                    # Extract system packages from RUN apt-get install commands
                    apt_matches = re.findall(r'apt-get install.*?(?=\n|\r|$)', dockerfile_content)
                    for match in apt_matches:
                        packages = re.findall(r'(\w+(?:-\w+)*)', match)
                        dependencies["system"].extend([pkg for pkg in packages if pkg not in ['apt-get', 'install', 'update', 'upgrade']])
            except Exception as e:
                dependencies["issues"].append(f"Failed to parse Dockerfile: {e}")
        
        return dependencies
    
    def _analyze_configuration(self, project_dir: str) -> Dict[str, Any]:
        """Analyze project configuration files"""
        config_info = {
            "config_files": [],
            "environment_files": [],
            "docker_files": [],
            "database_config": None,
            "port_configuration": None
        }
        
        # Find configuration files
        config_patterns = [
            "config.*", "*.config", "*.conf",
            ".env*", "environment.*"
        ]
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_dir)
                
                # Configuration files
                if any(Path(file).match(pattern) for pattern in config_patterns):
                    config_info["config_files"].append(rel_path)
                
                # Environment files
                if file.startswith('.env') or 'environment' in file.lower():
                    config_info["environment_files"].append(rel_path)
                
                # Docker files
                if file.lower().startswith('docker') or file == 'Dockerfile':
                    config_info["docker_files"].append(rel_path)
        
        # Try to detect database configuration
        config_info["database_config"] = self._detect_database_config(project_dir)
        
        # Try to detect port configuration
        config_info["port_configuration"] = self._detect_port_config(project_dir)
        
        return config_info
    
    def _detect_database_config(self, project_dir: str) -> Optional[Dict[str, Any]]:
        """Detect database configuration"""
        db_indicators = {
            "mongodb": ["mongodb://", "mongoose", "mongo"],
            "postgresql": ["postgresql://", "psycopg2", "pg"],
            "mysql": ["mysql://", "pymysql", "mysql2"],
            "sqlite": ["sqlite", ".db", ".sqlite3"],
            "redis": ["redis://", "redis"]
        }
        
        detected_dbs = []
        
        # Check configuration files
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(('.json', '.yml', '.yaml', '.env', '.py', '.js')):
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            for db_type, indicators in db_indicators.items():
                                if any(indicator in content for indicator in indicators):
                                    if db_type not in detected_dbs:
                                        detected_dbs.append(db_type)
                    except Exception:
                        continue
        
        return {"detected_databases": detected_dbs} if detected_dbs else None
    
    def _detect_port_config(self, project_dir: str) -> Optional[Dict[str, Any]]:
        """Detect port configuration"""
        port_patterns = [
            r'port.*?(\d+)',
            r'PORT.*?(\d+)',
            r'listen.*?(\d+)',
            r'server.*?(\d+)'
        ]
        
        detected_ports = []
        
        # Check main application files
        main_files = ['app.py', 'main.py', 'server.js', 'index.js', 'app.js']
        
        for file in main_files:
            file_path = os.path.join(project_dir, file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in port_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                try:
                                    port = int(match)
                                    if 1000 <= port <= 65535:  # Valid port range
                                        detected_ports.append(port)
                                except ValueError:
                                    continue
                except Exception:
                    continue
        
        return {"detected_ports": list(set(detected_ports))} if detected_ports else None
    
    def _identify_potential_issues(self, project_dir: str) -> List[Dict[str, str]]:
        """Identify potential deployment issues"""
        issues = []
        
        # Check for missing important files
        project_type = self.analysis_result.get("project_type", {})
        if project_type.get("primary") == "nodejs":
            structure = self.analysis_result.get("structure", {})
            important_files = structure.get("important_files", [])
            if "package.json" not in [os.path.basename(f) for f in important_files]:
                issues.append({
                    "type": "missing_file",
                    "severity": "high",
                    "description": "Missing package.json file for Node.js project"
                })
        
        elif project_type.get("primary") == "python":
            structure = self.analysis_result.get("structure", {})
            important_files = structure.get("important_files", [])
            has_requirements = any("requirements.txt" in f for f in important_files)
            has_setup = any("setup.py" in f for f in important_files)
            if not has_requirements and not has_setup:
                issues.append({
                    "type": "missing_file",
                    "severity": "medium",
                    "description": "Missing requirements.txt or setup.py for Python project"
                })
        
        # Check for hardcoded configurations
        hardcoded_patterns = [
            ("localhost", "Hardcoded localhost references found"),
            ("127.0.0.1", "Hardcoded local IP addresses found"),
            ("password", "Potential hardcoded passwords found"),
            ("secret", "Potential hardcoded secrets found")
        ]
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.json', '.yml', '.yaml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            for pattern, description in hardcoded_patterns:
                                if pattern in content:
                                    issues.append({
                                        "type": "hardcoded_config",
                                        "severity": "medium",
                                        "description": f"{description} in {os.path.relpath(file_path, project_dir)}"
                                    })
                                    break  # Only report once per file
                    except Exception:
                        continue
        
        # Check for missing environment configuration
        structure = self.analysis_result.get("structure", {})
        important_files = structure.get("important_files", [])
        env_files = [f for f in important_files if '.env' in f]
        if not env_files:
            issues.append({
                "type": "missing_env",
                "severity": "low",
                "description": "No environment configuration files found"
            })
        
        # Check for large files that might cause issues
        large_files = []
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                        large_files.append(os.path.relpath(file_path, project_dir))
                except OSError:
                    continue
        
        if large_files:
            issues.append({
                "type": "large_files",
                "severity": "medium",
                "description": f"Large files found that may cause deployment issues: {', '.join(large_files[:5])}"
            })
        
        return issues
    
    def _generate_recommendations(self):
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Recommendations based on project type
        project_type = self.analysis_result["project_type"]["primary"]
        
        if project_type == "nodejs":
            recommendations.append("Consider using PM2 for process management in production")
            if "express" in self.analysis_result["project_type"]["frameworks"]:
                recommendations.append("Ensure Express app binds to 0.0.0.0 for external access")
        
        elif project_type == "python":
            recommendations.append("Consider using Gunicorn or uWSGI for production deployment")
            if "django" in self.analysis_result["project_type"]["frameworks"]:
                recommendations.append("Set DEBUG=False and configure ALLOWED_HOSTS for production")
            elif "flask" in self.analysis_result["project_type"]["frameworks"]:
                recommendations.append("Use a production WSGI server instead of Flask's development server")
        
        # Recommendations based on detected issues
        for issue in self.analysis_result["potential_issues"]:
            if issue["type"] == "hardcoded_config":
                recommendations.append("Move hardcoded configurations to environment variables")
            elif issue["type"] == "missing_env":
                recommendations.append("Create environment configuration files for different deployment stages")
        
        # Database recommendations
        if self.analysis_result["configuration"]["database_config"]:
            dbs = self.analysis_result["configuration"]["database_config"]["detected_databases"]
            if dbs:
                recommendations.append(f"Ensure database services are available: {', '.join(dbs)}")
        
        # Port configuration recommendations
        if self.analysis_result["configuration"]["port_configuration"]:
            ports = self.analysis_result["configuration"]["port_configuration"]["detected_ports"]
            if ports:
                recommendations.append(f"Configure port binding for detected ports: {', '.join(map(str, ports))}")
        
        # General deployment recommendations
        recommendations.extend([
            "Add health check endpoints for monitoring",
            "Implement logging for debugging deployment issues",
            "Set up error handling for production environment",
            "Consider adding Docker support for consistent deployments"
        ])
        
        self.analysis_result["recommendations"] = recommendations
