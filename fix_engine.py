"""
Fix Engine for Bilman Deployment
Automatically fixes common deployment issues
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class FixEngine:
    def __init__(self):
        self.fixes_applied = []
        
    def apply_fixes(self, project_dir: str, analysis: Dict[str, Any]) -> bool:
        """Apply fixes based on project analysis"""
        logger.info("Starting automated fixes...")
        
        try:
            # Apply fixes based on project type
            project_type = analysis.get("project_type", {}).get("primary", "unknown")
            
            if project_type == "nodejs":
                self._fix_nodejs_issues(project_dir, analysis)
            elif project_type == "python":
                self._fix_python_issues(project_dir, analysis)
            elif project_type == "php":
                self._fix_php_issues(project_dir, analysis)
            
            # Apply generic fixes
            self._fix_port_binding(project_dir, analysis)
            self._fix_environment_config(project_dir, analysis)
            self._fix_hardcoded_configs(project_dir, analysis)
            self._create_startup_script(project_dir, analysis)
            
            logger.info(f"Applied {len(self.fixes_applied)} fixes")
            return len(self.fixes_applied) > 0
            
        except Exception as e:
            logger.error(f"Fix application failed: {e}")
            return False

    def _fix_nodejs_issues(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix Node.js specific issues"""
        logger.info("Applying Node.js fixes...")
        
        # Fix package.json scripts
        package_json_path = os.path.join(project_dir, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Ensure start script exists
                if "scripts" not in package_data:
                    package_data["scripts"] = {}
                
                if "start" not in package_data["scripts"]:
                    # Try to detect main file
                    main_file = package_data.get("main", "index.js")
                    if not os.path.exists(os.path.join(project_dir, main_file)):
                        # Look for common entry points
                        for entry in ["app.js", "server.js", "main.js", "index.js"]:
                            if os.path.exists(os.path.join(project_dir, entry)):
                                main_file = entry
                                break
                    
                    package_data["scripts"]["start"] = f"node {main_file}"
                    self.fixes_applied.append("Added start script to package.json")
                
                # Write updated package.json
                with open(package_json_path, 'w') as f:
                    json.dump(package_data, f, indent=2)
                    
            except Exception as e:
                logger.error(f"Failed to fix package.json: {e}")
        
        # Fix main application file for proper hosting
        main_files = ["app.js", "server.js", "index.js", "main.js"]
        for main_file in main_files:
            main_path = os.path.join(project_dir, main_file)
            if os.path.exists(main_path):
                self._fix_nodejs_main_file(main_path)
                break

    def _fix_nodejs_main_file(self, file_path: str):
        """Fix Node.js main file for proper deployment"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Fix port binding
            port_patterns = [
                (r'\.listen\(\s*(\d+)\s*\)', r'.listen(process.env.PORT || \1, "0.0.0.0")'),
                (r'\.listen\(\s*process\.env\.PORT\s*\|\|\s*(\d+)\s*\)', r'.listen(process.env.PORT || \1, "0.0.0.0")'),
            ]
            
            for pattern, replacement in port_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    break
            
            # Add default port if no listen call found
            if '.listen(' not in content and 'createServer' in content:
                # Add listen call at the end
                content += '\n\n// Added by deployment fix\nconst PORT = process.env.PORT || 3000;\napp.listen(PORT, "0.0.0.0", () => {\n  console.log(`Server running on port ${PORT}`);\n});\n'
                self.fixes_applied.append("Added proper port binding to Node.js app")
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                self.fixes_applied.append(f"Fixed port binding in {os.path.basename(file_path)}")
                
        except Exception as e:
            logger.error(f"Failed to fix Node.js main file: {e}")

    def _fix_python_issues(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix Python specific issues"""
        logger.info("Applying Python fixes...")
        
        # Fix main Python files
        main_files = ["app.py", "main.py", "server.py", "run.py"]
        for main_file in main_files:
            main_path = os.path.join(project_dir, main_file)
            if os.path.exists(main_path):
                self._fix_python_main_file(main_path, analysis)
        
        # Create run script if needed
        if not any(os.path.exists(os.path.join(project_dir, f)) for f in main_files):
            self._create_python_run_script(project_dir)

    def _fix_python_main_file(self, file_path: str, analysis: Dict[str, Any]):
        """Fix Python main file for proper deployment"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            frameworks = analysis.get("project_type", {}).get("frameworks", [])
            
            # Fix Flask applications
            if "flask" in frameworks:
                # Fix host and port binding
                run_patterns = [
                    (r'app\.run\(\)', 'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))'),
                    (r'app\.run\(debug=True\)', 'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)'),
                    (r'app\.run\(host=[\'"]localhost[\'"]\)', 'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))'),
                ]
                
                for pattern, replacement in run_patterns:
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        self.fixes_applied.append("Fixed Flask app.run() for deployment")
                        break
                
                # Add os import if needed
                if 'os.environ.get("PORT"' in content and 'import os' not in content:
                    content = 'import os\n' + content
                    self.fixes_applied.append("Added os import for PORT environment variable")
            
            # Fix Django applications
            elif "django" in frameworks:
                # Look for settings.py
                settings_path = os.path.join(os.path.dirname(file_path), "settings.py")
                if os.path.exists(settings_path):
                    self._fix_django_settings(settings_path)
            
            # Fix FastAPI applications
            elif "fastapi" in frameworks:
                # Fix uvicorn run configuration
                if 'uvicorn.run(' in content:
                    uvicorn_pattern = r'uvicorn\.run\([^)]*\)'
                    if re.search(uvicorn_pattern, content):
                        content = re.sub(
                            uvicorn_pattern,
                            'uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))',
                            content
                        )
                        self.fixes_applied.append("Fixed FastAPI uvicorn configuration")
                
                # Add os import if needed
                if 'os.environ.get("PORT"' in content and 'import os' not in content:
                    content = 'import os\n' + content
            
            # Generic Python app fixes
            if '__name__ == "__main__"' in content:
                # Add basic server setup if none exists
                if 'app.run(' not in content and 'uvicorn.run(' not in content and '.serve_forever()' not in content:
                    content += '\n\n# Added by deployment fix\nif __name__ == "__main__":\n    import os\n    port = int(os.environ.get("PORT", 8000))\n    print(f"Starting server on port {port}")\n'
                    self.fixes_applied.append("Added basic server startup code")
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to fix Python main file: {e}")

    def _fix_django_settings(self, settings_path: str):
        """Fix Django settings for deployment"""
        try:
            with open(settings_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Fix ALLOWED_HOSTS
            if 'ALLOWED_HOSTS = []' in content:
                content = content.replace(
                    'ALLOWED_HOSTS = []',
                    'ALLOWED_HOSTS = ["*"]  # Fixed for deployment'
                )
                self.fixes_applied.append("Fixed Django ALLOWED_HOSTS setting")
            
            # Fix DEBUG setting
            if 'DEBUG = True' in content:
                content = content.replace(
                    'DEBUG = True',
                    'DEBUG = os.environ.get("DEBUG", "False").lower() == "true"'
                )
                self.fixes_applied.append("Fixed Django DEBUG setting for production")
                
                # Add os import if needed
                if 'import os' not in content:
                    content = 'import os\n' + content
            
            # Write back if changed
            if content != original_content:
                with open(settings_path, 'w') as f:
                    f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to fix Django settings: {e}")

    def _fix_php_issues(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix PHP specific issues"""
        logger.info("Applying PHP fixes...")
        
        # Create .htaccess if needed
        htaccess_path = os.path.join(project_dir, ".htaccess")
        if not os.path.exists(htaccess_path):
            htaccess_content = """# Added by deployment fix
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.+)$ index.php [QSA,L]
"""
            with open(htaccess_path, 'w') as f:
                f.write(htaccess_content)
            self.fixes_applied.append("Created .htaccess file for PHP application")

    def _fix_port_binding(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix port binding issues across all file types"""
        logger.info("Fixing port binding issues...")
        
        # Common patterns to look for and fix
        problematic_patterns = [
            ("localhost", "0.0.0.0"),
            ("127.0.0.1", "0.0.0.0"),
        ]
        
        # File extensions to check
        extensions = ['.py', '.js', '.php', '.rb', '.go']
        
        for root, dirs, files in os.walk(project_dir):
            # Skip node_modules and other irrelevant directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        self._fix_file_bindings(file_path, problematic_patterns)
                    except Exception as e:
                        logger.warning(f"Failed to fix bindings in {file_path}: {e}")

    def _fix_file_bindings(self, file_path: str, patterns: List[tuple]):
        """Fix binding patterns in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            for old_pattern, new_pattern in patterns:
                # Only replace in context of host/bind/listen configurations
                host_contexts = [
                    rf'host\s*[=:]\s*["\']?{re.escape(old_pattern)}["\']?',
                    rf'bind\s*[=:]\s*["\']?{re.escape(old_pattern)}["\']?',
                    rf'listen\s*[=:]\s*["\']?{re.escape(old_pattern)}["\']?',
                ]
                
                for context in host_contexts:
                    if re.search(context, content, re.IGNORECASE):
                        content = re.sub(
                            context,
                            lambda m: m.group(0).replace(old_pattern, new_pattern),
                            content,
                            flags=re.IGNORECASE
                        )
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f"Fixed host binding in {os.path.relpath(file_path)}")
                
        except Exception as e:
            logger.warning(f"Failed to fix bindings in {file_path}: {e}")

    def _fix_environment_config(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix environment configuration issues"""
        logger.info("Fixing environment configuration...")
        
        # Create .env file if it doesn't exist
        env_files = analysis.get("configuration", {}).get("environment_files", [])
        if not env_files:
            env_path = os.path.join(project_dir, ".env")
            env_content = """# Environment Configuration - Added by deployment fix
NODE_ENV=production
DEBUG=false
PORT=8000
HOST=0.0.0.0
"""
            with open(env_path, 'w') as f:
                f.write(env_content)
            self.fixes_applied.append("Created .env file with deployment configuration")

    def _fix_hardcoded_configs(self, project_dir: str, analysis: Dict[str, Any]):
        """Fix hardcoded configuration values"""
        logger.info("Fixing hardcoded configurations...")
        
        # This is a simplified fix - in practice, you'd want more sophisticated detection
        issues = analysis.get("potential_issues", [])
        hardcoded_issues = [issue for issue in issues if issue["type"] == "hardcoded_config"]
        
        if hardcoded_issues:
            # Create a configuration guide file
            guide_path = os.path.join(project_dir, "DEPLOYMENT_NOTES.md")
            guide_content = """# Deployment Configuration Notes

## Hardcoded Values Detected
The following files contain hardcoded values that should be moved to environment variables:

"""
            for issue in hardcoded_issues:
                guide_content += f"- {issue['description']}\n"
            
            guide_content += """
## Recommended Actions
1. Move hardcoded values to environment variables
2. Use process.env.VARIABLE_NAME (Node.js) or os.environ.get('VARIABLE_NAME') (Python)
3. Update configuration files to use environment variables

## Environment Variables to Set
- DATABASE_URL
- SECRET_KEY
- API_KEYS
- PORT
- HOST
"""
            
            with open(guide_path, 'w') as f:
                f.write(guide_content)
            self.fixes_applied.append("Created deployment configuration guide")

    def _create_startup_script(self, project_dir: str, analysis: Dict[str, Any]):
        """Create startup script for the application"""
        logger.info("Creating startup script...")
        
        project_type = analysis.get("project_type", {}).get("primary", "unknown")
        
        if project_type == "nodejs":
            self._create_nodejs_startup(project_dir)
        elif project_type == "python":
            self._create_python_startup(project_dir, analysis)

    def _create_nodejs_startup(self, project_dir: str):
        """Create Node.js startup script"""
        start_script_path = os.path.join(project_dir, "start.sh")
        start_content = """#!/bin/bash
# Node.js Application Startup Script - Added by deployment fix

echo "Starting Node.js application..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the application
echo "Starting server..."
npm start
"""
        
        with open(start_script_path, 'w') as f:
            f.write(start_content)
        
        # Make executable
        os.chmod(start_script_path, 0o755)
        self.fixes_applied.append("Created Node.js startup script")

    def _create_python_startup(self, project_dir: str, analysis: Dict[str, Any]):
        """Create Python startup script"""
        start_script_path = os.path.join(project_dir, "start.sh")
        frameworks = analysis.get("project_type", {}).get("frameworks", [])
        
        if "django" in frameworks:
            start_content = """#!/bin/bash
# Django Application Startup Script - Added by deployment fix

echo "Starting Django application..."

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
"""
        elif "flask" in frameworks:
            start_content = """#!/bin/bash
# Flask Application Startup Script - Added by deployment fix

echo "Starting Flask application..."

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the application
echo "Starting server..."
python app.py
"""
        else:
            start_content = """#!/bin/bash
# Python Application Startup Script - Added by deployment fix

echo "Starting Python application..."

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Find and start main application
if [ -f "main.py" ]; then
    python main.py
elif [ -f "app.py" ]; then
    python app.py
elif [ -f "server.py" ]; then
    python server.py
else
    echo "No main application file found"
    exit 1
fi
"""
        
        with open(start_script_path, 'w') as f:
            f.write(start_content)
        
        # Make executable
        os.chmod(start_script_path, 0o755)
        self.fixes_applied.append("Created Python startup script")

    def _create_python_run_script(self, project_dir: str):
        """Create a basic Python run script if none exists"""
        run_script_path = os.path.join(project_dir, "run.py")
        run_content = """#!/usr/bin/env python3
# Basic run script - Added by deployment fix

import os
import sys
from pathlib import Path

def find_main_module():
    \"\"\"Find the main application module\"\"\"
    candidates = ['app.py', 'main.py', 'server.py', 'wsgi.py']
    
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate.replace('.py', '')
    
    return None

def main():
    \"\"\"Main entry point\"\"\"
    print("Starting application...")
    
    # Set environment variables
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    
    # Try to find and import main module
    main_module = find_main_module()
    if main_module:
        try:
            __import__(main_module)
            print(f"Started {main_module}")
        except Exception as e:
            print(f"Failed to start {main_module}: {e}")
            sys.exit(1)
    else:
        print("No main application module found")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        with open(run_script_path, 'w') as f:
            f.write(run_content)
        
        self.fixes_applied.append("Created Python run script")

    def get_fixes_applied(self) -> List[str]:
        """Get list of fixes that were applied"""
        return self.fixes_applied.copy()
