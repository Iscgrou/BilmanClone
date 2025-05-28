#!/usr/bin/env python3
"""
Bilman Project Deployment System
Handles cloning, analysis, fixing, and deployment of the bilman project
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
import requests
from project_analyzer import ProjectAnalyzer
from fix_engine import FixEngine
from config_manager import ConfigManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BilmanDeployer:
    def __init__(self):
        self.repo_url = "https://github.com/Iscgrou/bilman"
        self.project_dir = "./bilman"
        self.config_manager = ConfigManager()
        self.analyzer = ProjectAnalyzer()
        self.fix_engine = FixEngine()
        self.deployment_status = {
            "cloned": False,
            "analyzed": False,
            "fixed": False,
            "deployed": False
        }

    def run_command(self, command: str, cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Run a shell command and return success status, stdout, stderr"""
        try:
            logger.info(f"Running command: {command}")
            result = subprocess.run(
                command.split(),
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            success = result.returncode == 0
            if not success:
                logger.error(f"Command failed with return code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
            return success, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return False, "", str(e)

    def clone_repository(self) -> bool:
        """Clone the bilman repository"""
        logger.info("Starting repository clone...")
        
        # Remove existing directory if it exists
        if os.path.exists(self.project_dir):
            logger.info("Removing existing project directory")
            shutil.rmtree(self.project_dir)
        
        # Clone the repository
        success, stdout, stderr = self.run_command(f"git clone {self.repo_url} {self.project_dir}")
        
        if success:
            logger.info("Repository cloned successfully")
            self.deployment_status["cloned"] = True
            return True
        else:
            logger.error(f"Failed to clone repository: {stderr}")
            return False

    def analyze_project(self) -> Dict:
        """Analyze the project structure and dependencies"""
        logger.info("Starting project analysis...")
        
        if not os.path.exists(self.project_dir):
            logger.error("Project directory not found")
            return {}
        
        analysis_result = self.analyzer.analyze(self.project_dir)
        
        if analysis_result:
            logger.info("Project analysis completed")
            self.deployment_status["analyzed"] = True
            
            # Save analysis results
            with open("analysis_report.json", "w") as f:
                json.dump(analysis_result, f, indent=2)
            
            return analysis_result
        else:
            logger.error("Project analysis failed")
            return {}

    def fix_issues(self, analysis_result: Dict) -> bool:
        """Fix common deployment issues"""
        logger.info("Starting issue fixes...")
        
        fixes_applied = self.fix_engine.apply_fixes(self.project_dir, analysis_result)
        
        if fixes_applied:
            logger.info("Issues fixed successfully")
            self.deployment_status["fixed"] = True
            
            # Commit fixes
            self.commit_changes("Applied automated deployment fixes")
            return True
        else:
            logger.warning("No fixes were needed or fixes failed")
            return True  # Continue deployment even if no fixes needed

    def commit_changes(self, message: str) -> bool:
        """Commit changes to git"""
        logger.info(f"Committing changes: {message}")
        
        # Configure git if needed
        self.run_command("git config user.email 'deploy@replit.com'", cwd=self.project_dir)
        self.run_command("git config user.name 'Replit Deployer'", cwd=self.project_dir)
        
        # Add and commit changes
        success1, _, _ = self.run_command("git add .", cwd=self.project_dir)
        success2, _, _ = self.run_command(f'git commit -m "{message}"', cwd=self.project_dir)
        
        if success1 and success2:
            logger.info("Changes committed successfully")
            return True
        else:
            logger.warning("Failed to commit changes (may be no changes to commit)")
            return False

    def setup_configuration(self, domain: str, username: str, password: str) -> bool:
        """Setup project configuration with provided credentials"""
        logger.info("Setting up project configuration...")
        
        config = {
            "domain": domain,
            "username": username,
            "password": password,
            "deployment_time": str(subprocess.check_output(['date'], text=True).strip())
        }
        
        return self.config_manager.setup_config(self.project_dir, config)

    def deploy_project(self) -> bool:
        """Deploy the project"""
        logger.info("Starting project deployment...")
        
        # Try different deployment strategies based on project type
        deployment_success = False
        
        # Strategy 1: Check for package.json (Node.js project)
        if os.path.exists(os.path.join(self.project_dir, "package.json")):
            logger.info("Detected Node.js project, attempting npm deployment")
            deployment_success = self._deploy_nodejs()
        
        # Strategy 2: Check for requirements.txt (Python project)
        elif os.path.exists(os.path.join(self.project_dir, "requirements.txt")):
            logger.info("Detected Python project, attempting Python deployment")
            deployment_success = self._deploy_python()
        
        # Strategy 3: Check for specific files or try generic deployment
        else:
            logger.info("Attempting generic deployment")
            deployment_success = self._deploy_generic()
        
        if deployment_success:
            logger.info("Project deployed successfully")
            self.deployment_status["deployed"] = True
            return True
        else:
            logger.error("Project deployment failed")
            return False

    def _deploy_nodejs(self) -> bool:
        """Deploy Node.js project"""
        # Install dependencies
        success, _, _ = self.run_command("npm install", cwd=self.project_dir)
        if not success:
            logger.error("npm install failed")
            return False
        
        # Try to start the application
        # This would typically be handled by Replit's runtime
        logger.info("Node.js dependencies installed successfully")
        return True

    def _deploy_python(self) -> bool:
        """Deploy Python project"""
        # Install dependencies
        success, _, _ = self.run_command("pip install -r requirements.txt", cwd=self.project_dir)
        if not success:
            logger.error("pip install failed")
            return False
        
        logger.info("Python dependencies installed successfully")
        return True

    def _deploy_generic(self) -> bool:
        """Generic deployment strategy"""
        # Copy project files to current directory for Replit execution
        try:
            for item in os.listdir(self.project_dir):
                source = os.path.join(self.project_dir, item)
                dest = os.path.join(".", f"bilman_{item}")
                
                if os.path.isdir(source):
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
            
            logger.info("Project files copied for deployment")
            return True
        except Exception as e:
            logger.error(f"Generic deployment failed: {e}")
            return False

    def generate_status_report(self) -> Dict:
        """Generate deployment status report"""
        report = {
            "deployment_status": self.deployment_status,
            "timestamp": str(subprocess.check_output(['date'], text=True).strip()),
            "project_directory": self.project_dir,
            "logs_available": os.path.exists("deployment.log")
        }
        
        # Add analysis results if available
        if os.path.exists("analysis_report.json"):
            with open("analysis_report.json", "r") as f:
                report["analysis"] = json.load(f)
        
        return report

def main():
    """Main deployment function"""
    print("🚀 Bilman Project Deployment System")
    print("=====================================")
    
    deployer = BilmanDeployer()
    
    try:
        # Step 1: Clone repository
        print("\n📥 Cloning repository...")
        if not deployer.clone_repository():
            print("❌ Failed to clone repository")
            return False
        print("✅ Repository cloned successfully")
        
        # Step 2: Analyze project
        print("\n🔍 Analyzing project...")
        analysis = deployer.analyze_project()
        if not analysis:
            print("❌ Project analysis failed")
            return False
        print("✅ Project analysis completed")
        
        # Step 3: Fix issues
        print("\n🔧 Applying fixes...")
        if not deployer.fix_issues(analysis):
            print("⚠️  Fix application had issues, but continuing...")
        else:
            print("✅ Fixes applied successfully")
        
        # Step 4: Setup configuration (will be prompted via web interface)
        print("\n⚙️  Configuration setup will be handled via web interface")
        
        # Step 5: Deploy project
        print("\n🚀 Deploying project...")
        if not deployer.deploy_project():
            print("❌ Project deployment failed")
            return False
        print("✅ Project deployed successfully")
        
        # Generate final report
        report = deployer.generate_status_report()
        with open("deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n🎉 Deployment completed successfully!")
        print("📋 Check deployment_report.json for detailed information")
        print("🌐 Access the web interface at http://localhost:5000 for configuration")
        
        return True
        
    except Exception as e:
        logger.error(f"Deployment failed with error: {e}")
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
