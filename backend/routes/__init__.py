from .api import api_bp
from .health import health_bp

def register_routes(app, flashcard_service=None, session_service=None, validator=None):
    """Register all route blueprints with the Flask app and inject dependencies."""
    
    # Attach services + validator to api_bp
    api_bp.flashcard_service = flashcard_service
    api_bp.session_service = session_service
    api_bp.validator = validator
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)