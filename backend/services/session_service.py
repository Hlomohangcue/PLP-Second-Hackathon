import logging
from typing import Dict, Optional
from models import Session
from flask import current_app

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions."""
    
    def create_session(self) -> Dict:
        """Create a new user session."""
        
        try:
            timeout_days = current_app.config.get('SESSION_TIMEOUT_DAYS', 30)
            session = Session.create_session(timeout_days=timeout_days)
            
            logger.info(f"Created new session: {session.id}")
            
            return {
                'success': True,
                'session': session.to_dict(),
                'message': 'Session created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session(self, session_id: str) -> Dict:
        """Get session information."""
        
        try:
            session = Session.get_active_session(session_id)
            
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found or expired'
                }
            
            return {
                'success': True,
                'session': session.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extend_session(self, session_id: str, days: int = 30) -> Dict:
        """Extend session expiration."""
        
        try:
            session = Session.get_active_session(session_id)
            
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found or expired'
                }
            
            session.extend_session(days=days)
            
            logger.info(f"Extended session {session_id} by {days} days")
            
            return {
                'success': True,
                'session': session.to_dict(),
                'message': f'Session extended by {days} days'
            }
            
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def deactivate_session(self, session_id: str) -> Dict:
        """Deactivate a session."""
        
        try:
            session = Session.query.filter_by(id=session_id).first()
            
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
            
            session.deactivate()
            
            logger.info(f"Deactivated session: {session_id}")
            
            return {
                'success': True,
                'message': 'Session deactivated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deactivating session {session_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_expired_sessions(self) -> Dict:
        """Clean up expired sessions."""
        
        try:
            cleaned_count = Session.cleanup_expired_sessions()
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            
            return {
                'success': True,
                'cleaned_sessions': cleaned_count,
                'message': f'Cleaned up {cleaned_count} expired sessions'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if session is active and not expired."""
        
        try:
            session = Session.get_active_session(session_id)
            return session is not None
            
        except Exception as e:
            logger.error(f"Error validating session {session_id}: {str(e)}")
            return False