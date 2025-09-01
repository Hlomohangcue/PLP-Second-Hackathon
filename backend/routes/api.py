# routes/api.py
from flask import Blueprint, request, jsonify, current_app
import logging

from utils.helpers import create_json_response, sanitize_input

# Create blueprint
api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

# -------------------------------
# Helper Functions
# -------------------------------
def get_session_id():
    """Get session ID from request headers or request body."""
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        data = request.get_json(silent=True)
        if data:
            session_id = data.get('session_id')
    return session_id


# -------------------------------
# Session Management Routes
# -------------------------------
@api_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new user session."""
    try:
        session_service = api_bp.session_service
        result = session_service.create_session()

        if result['success']:
            return create_json_response(success=True, data=result['session'], message=result['message'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=500)

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return create_json_response(success=False, error="Failed to create session", status_code=500)


@api_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session information."""
    try:
        session_service = api_bp.session_service
        validator = api_bp.validator

        validation_result = validator.validate_session_id(session_id)
        if not validation_result['valid']:
            return create_json_response(success=False, error=validation_result['error'], status_code=400)

        result = session_service.get_session(session_id)
        if result['success']:
            return create_json_response(success=True, data=result['session'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to retrieve session", status_code=500)


@api_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Deactivate a session."""
    try:
        session_service = api_bp.session_service
        result = session_service.deactivate_session(session_id)

        if result['success']:
            return create_json_response(success=True, message=result['message'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to delete session", status_code=500)


# -------------------------------
# Flashcard Routes
# -------------------------------
@api_bp.route('/process-notes', methods=['POST'])
def process_notes():
    """Process study notes and generate flashcards."""
    try:
        flashcard_service = api_bp.flashcard_service
        session_service = api_bp.session_service
        validator = api_bp.validator

        data = request.get_json()
        if not data:
            return create_json_response(success=False, error="No JSON data provided", status_code=400)

        # Get or create session
        session_id = data.get('session_id') or get_session_id()
        if not session_id:
            session_result = session_service.create_session()
            if not session_result['success']:
                return create_json_response(success=False, error="Failed to create session", status_code=500)
            session_id = session_result['session']['id']

        # Validate notes content
        content = data.get('notes', '').strip()
        validation_result = validator.validate_content(content)
        if not validation_result['valid']:
            return create_json_response(success=False, error=validation_result['error'], status_code=400)

        # Validate title
        title = data.get('title', '').strip() if data.get('title') else None
        if title:
            title_validation = validator.validate_title(title)
            if not title_validation['valid']:
                return create_json_response(success=False, error=title_validation['error'], status_code=400)
            title = title_validation['cleaned_title']

        # Sanitize input
        clean_content = sanitize_input(validation_result['cleaned_content'])
        logger.info(f"Processing notes for session {session_id}, content length: {len(clean_content)}")

        result = flashcard_service.create_flashcard_set(
            session_id=session_id, content=clean_content, title=title
        )

        if result['success']:
            return create_json_response(
                success=True,
                data={
                    'session_id': session_id,
                    'flashcard_set': result['flashcard_set'],
                    'generation_method': result['generation_method']
                },
                message=result['message']
            )
        else:
            return create_json_response(success=False, error=result['error'], status_code=500)

    except Exception as e:
        logger.error(f"Error processing notes: {str(e)}")
        return create_json_response(success=False, error="Unexpected error while processing notes", status_code=500)


@api_bp.route('/flashcards', methods=['GET'])
def get_flashcards():
    """Get all flashcard sets for a session."""
    try:
        flashcard_service = api_bp.flashcard_service
        session_id = get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        result = flashcard_service.get_session_flashcard_sets(session_id)
        if result['success']:
            return create_json_response(success=True, data={
                'flashcard_sets': result['flashcard_sets'],
                'count': result['count']
            })
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error retrieving flashcards: {str(e)}")
        return create_json_response(success=False, error="Failed to retrieve flashcards", status_code=500)


@api_bp.route('/flashcards/<set_id>', methods=['GET'])
def get_flashcard_set(set_id):
    """Get a specific flashcard set."""
    try:
        flashcard_service = api_bp.flashcard_service
        session_id = get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        result = flashcard_service.get_flashcard_set(set_id, session_id)
        if result['success']:
            return create_json_response(success=True, data=result['flashcard_set'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error retrieving flashcard set {set_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to retrieve flashcard set", status_code=500)


@api_bp.route('/flashcards/<set_id>', methods=['PUT'])
def update_flashcard_set(set_id):
    """Update flashcard set (currently only title)."""
    try:
        flashcard_service = api_bp.flashcard_service
        validator = api_bp.validator

        data = request.get_json()
        session_id = data.get('session_id') or get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        new_title = data.get('title', '').strip()
        if not new_title:
            return create_json_response(success=False, error="Title is required", status_code=400)

        # Validate title
        title_validation = validator.validate_title(new_title)
        if not title_validation['valid']:
            return create_json_response(success=False, error=title_validation['error'], status_code=400)

        result = flashcard_service.update_flashcard_set_title(
            set_id, session_id, title_validation['cleaned_title']
        )

        if result['success']:
            return create_json_response(success=True, data=result['flashcard_set'], message=result['message'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error updating flashcard set {set_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to update flashcard set", status_code=500)


@api_bp.route('/flashcards/<set_id>', methods=['DELETE'])
def delete_flashcard_set(set_id):
    """Delete a flashcard set."""
    try:
        flashcard_service = api_bp.flashcard_service
        session_id = get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        result = flashcard_service.delete_flashcard_set(set_id, session_id)
        if result['success']:
            return create_json_response(success=True, message=result['message'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error deleting flashcard set {set_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to delete flashcard set", status_code=500)


@api_bp.route('/flashcards/<set_id>/study', methods=['POST'])
def record_study_session(set_id):
    """Record a study session with performance data."""
    try:
        flashcard_service = api_bp.flashcard_service

        data = request.get_json()
        session_id = data.get('session_id') or get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        cards_studied = data.get('cards_studied', [])
        if not isinstance(cards_studied, list):
            return create_json_response(success=False, error="Invalid cards_studied data", status_code=400)

        result = flashcard_service.record_study_session(set_id, session_id, cards_studied)
        if result['success']:
            return create_json_response(success=True, message=result['message'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error recording study session for set {set_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to record study session", status_code=500)


@api_bp.route('/flashcards/<set_id>/statistics', methods=['GET'])
def get_study_statistics(set_id):
    """Get study statistics for a flashcard set."""
    try:
        flashcard_service = api_bp.flashcard_service
        session_id = get_session_id()

        if not session_id:
            return create_json_response(success=False, error="Session ID required", status_code=400)

        result = flashcard_service.get_study_statistics(set_id, session_id)
        if result['success']:
            return create_json_response(success=True, data=result['statistics'])
        else:
            return create_json_response(success=False, error=result['error'], status_code=404)

    except Exception as e:
        logger.error(f"Error retrieving statistics for set {set_id}: {str(e)}")
        return create_json_response(success=False, error="Failed to retrieve statistics", status_code=500)


# -------------------------------
# Error Handlers
# -------------------------------
@api_bp.errorhandler(429)
def ratelimit_handler(e):
    return create_json_response(success=False, error="Rate limit exceeded. Please try again later.", status_code=429)


@api_bp.errorhandler(404)
def not_found_handler(e):
    return create_json_response(success=False, error="Endpoint not found", status_code=404)


@api_bp.errorhandler(500)
def internal_error_handler(e):
    return create_json_response(success=False, error="Internal server error", status_code=500)
