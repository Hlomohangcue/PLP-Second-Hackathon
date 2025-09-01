from flask import Blueprint, current_app
from models.base import db
from services import SessionService
from utils.helpers import create_json_response
import logging

health_bp = Blueprint('health', __name__)
session_service = SessionService()
logger = logging.getLogger(__name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    
    try:
        return create_json_response(
            success=True,
            data={
                'status': 'healthy',
                'service': 'AI Study Buddy API',
                'version': '1.0.0'
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_json_response(
            success=False,
            error="Health check failed",
            status_code=500
        )

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check including dependencies."""
    
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        overall_healthy = False
    
    # Hugging Face API token check
    hf_token = current_app.config.get('HUGGING_FACE_API_TOKEN')
    if hf_token:
        health_status['checks']['hugging_face_token'] = {
            'status': 'healthy',
            'message': 'API token configured'
        }
    else:
        health_status['checks']['hugging_face_token'] = {
            'status': 'warning',
            'message': 'API token not configured, using fallback generation'
        }
    
    # Session cleanup check
    try:
        cleanup_result = session_service.cleanup_expired_sessions()
        health_status['checks']['session_cleanup'] = {
            'status': 'healthy',
            'message': f'Cleaned up {cleanup_result["cleaned_sessions"]} expired sessions'
        }
    except Exception as e:
        health_status['checks']['session_cleanup'] = {
            'status': 'warning',
            'message': f'Session cleanup issue: {str(e)}'
        }
    
    # Set overall status
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
    elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
        health_status['status'] = 'degraded'
    
    status_code = 200 if overall_healthy else 503
    
    return create_json_response(
        success=overall_healthy,
        data=health_status,
        status_code=status_code
    )

@health_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working."""
    
    try:
        return create_json_response(
            success=True,
            data={
                'message': 'API is working!',
                'hugging_face_token_set': bool(current_app.config.get('HUGGING_FACE_API_TOKEN')),
                'database_url': current_app.config['SQLALCHEMY_DATABASE_URI']
            }
        )
    except Exception as e:
        logger.error(f"Test endpoint failed: {str(e)}")
        return create_json_response(
            success=False,
            error="Test failed",
            status_code=500
        )