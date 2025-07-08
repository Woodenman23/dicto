import logging
import os
from typing import Dict, Any
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)
    
    # Enable CORS for frontend communication
    CORS(app)
    
    # Set base path for deployment context
    base_path = os.environ.get('BASE_PATH', '')
    app.config['BASE_PATH'] = base_path
    
    @app.context_processor
    def inject_base_path() -> Dict[str, Any]:
        return dict(base_path=app.config['BASE_PATH'])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register blueprints
    from website.views import views
    app.register_blueprint(views, url_prefix="/")
    
    logger.info("Dicto Flask app created successfully")
    return app