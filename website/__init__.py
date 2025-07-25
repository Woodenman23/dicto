import logging
import os
import secrets
from typing import Dict, Any
from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging with environment variable support
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Initialize Prometheus metrics (automatically adds /metrics endpoint)
    metrics = PrometheusMetrics(app)
    
    # Add custom metrics
    metrics.info('app_info', 'Application info', version='1.0')
    
    # Enable CORS for frontend communication - restrict to specific origins
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5005,http://127.0.0.1:5005').split(',')
    CORS(app, origins=allowed_origins)
    
    # Set base path for deployment context
    base_path = os.environ.get('BASE_PATH', '')
    app.config['BASE_PATH'] = base_path
    
    @app.context_processor
    def inject_base_path() -> Dict[str, Any]:
        return dict(base_path=app.config['BASE_PATH'])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register blueprints
    from website.views import views
    app.register_blueprint(views, url_prefix="/")
    
    logger.info("Dicto Flask app created successfully")
    return app