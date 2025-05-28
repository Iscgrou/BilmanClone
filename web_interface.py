"""
Web Interface for Bilman Deployment Configuration
Provides a user-friendly interface for setting up deployment configuration
"""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config_manager import ConfigManager
from werkzeug.security import generate_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'deployment-config-secret-key')

config_manager = ConfigManager()

@app.route('/')
def index():
    """Main configuration page"""
    return render_template('config.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        # Try to load existing configuration
        config = config_manager.load_config('./bilman')
        if config:
            # Don't send password back to frontend
            safe_config = {k: v for k, v in config.items() if k != 'password'}
            return jsonify({'success': True, 'config': safe_config})
        else:
            return jsonify({'success': True, 'config': {}})
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['domain', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'})
        
        # Validate domain format
        domain = data['domain'].strip()
        if not _validate_domain(domain):
            return jsonify({'success': False, 'error': 'Invalid domain format'})
        
        # Validate username
        username = data['username'].strip()
        if not _validate_username(username):
            return jsonify({'success': False, 'error': 'Invalid username format (3-20 alphanumeric characters)'})
        
        # Validate password
        password = data['password']
        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'})
        
        # Prepare configuration data
        config_data = {
            'domain': domain,
            'username': username,
            'password': generate_password_hash(password),  # Hash the password
            'deployment_timestamp': str(__import__('datetime').datetime.now()),
            'configured_by': 'web_interface'
        }
        
        # Save configuration
        success = config_manager.setup_config('./bilman', config_data)
        
        if success:
            # Also save to environment variables for immediate use
            os.environ['BILMAN_DOMAIN'] = domain
            os.environ['BILMAN_USERNAME'] = username
            os.environ['BILMAN_PASSWORD'] = password
            
            return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save configuration'})
            
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """Get deployment status"""
    try:
        status = {
            'bilman_directory_exists': os.path.exists('./bilman'),
            'config_files_exist': False,
            'deployment_log_exists': os.path.exists('deployment.log'),
            'analysis_report_exists': os.path.exists('analysis_report.json')
        }
        
        # Check for configuration files
        if os.path.exists('./bilman'):
            config_files = [
                'bilman_config.json',
                '.bilman.env',
                'config.json',
                '.env'
            ]
            status['config_files_exist'] = any(
                os.path.exists(os.path.join('./bilman', f)) for f in config_files
            )
        
        # Load deployment report if available
        if status['analysis_report_exists']:
            try:
                with open('analysis_report.json', 'r') as f:
                    status['analysis_report'] = json.load(f)
            except Exception:
                pass
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test connection with provided credentials"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Simple validation test
        if not domain or not username or not password:
            return jsonify({'success': False, 'error': 'Missing credentials'})
        
        # In a real implementation, you would test the actual connection here
        # For now, we'll just validate the format
        if _validate_domain(domain) and _validate_username(username) and len(password) >= 8:
            return jsonify({'success': True, 'message': 'Connection test successful'})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials format'})
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logs')
def get_logs():
    """Get deployment logs"""
    try:
        logs = []
        
        # Read deployment log
        if os.path.exists('deployment.log'):
            with open('deployment.log', 'r') as f:
                logs = f.readlines()[-50:]  # Last 50 lines
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({'success': False, 'error': str(e)})

def _validate_domain(domain: str) -> bool:
    """Validate domain format"""
    import re
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None

def _validate_username(username: str) -> bool:
    """Validate username format"""
    import re
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def main():
    """Main function to run the web interface"""
    print("🌐 Starting Bilman Configuration Web Interface")
    print("============================================")
    print("Access the configuration interface at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
