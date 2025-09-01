import logging
from typing import List, Dict, Optional
from models import FlashcardSet, Flashcard, Session
from services.ai_service import AIService
from utils.validators import ContentValidator

logger = logging.getLogger(__name__)

class FlashcardService:
    """Service for managing flashcard operations."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.validator = ContentValidator()
    
    def create_flashcard_set(self, session_id: str, content: str, title: Optional[str] = None) -> Dict:
        """Create a new flashcard set from content."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Validate content
            validation_result = self.validator.validate_content(content)
            if not validation_result['valid']:
                raise ValueError(validation_result['error'])
            
            logger.info(f"Creating flashcard set for session {session_id}")
            
            # Generate flashcards using AI service
            flashcards_data = self.ai_service.generate_flashcards(content)
            
            if not flashcards_data:
                raise ValueError("Failed to generate flashcards from content")
            
            # Validate generated flashcards
            validated_flashcards = self.ai_service.validate_flashcards(flashcards_data)
            
            if len(validated_flashcards) < 2:
                raise ValueError("Could not generate sufficient quality flashcards")
            
            # Determine generation method
            generation_method = 'ai' if self.ai_service.api_token else 'fallback'
            
            # Create flashcard set
            flashcard_set = FlashcardSet.create_set_with_flashcards(
                session_id=session_id,
                original_content=content,
                flashcards_data=validated_flashcards,
                title=title,
                generation_method=generation_method
            )
            
            logger.info(f"Created flashcard set {flashcard_set.id} with {len(validated_flashcards)} cards")
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'flashcard_set': flashcard_set.to_dict(include_flashcards=True),
                'generation_method': generation_method,
                'message': f'Generated {len(validated_flashcards)} flashcards successfully!'
            }
            
        except Exception as e:
            logger.error(f"Error creating flashcard set: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_flashcard_set(self, set_id: str, session_id: str) -> Dict:
        """Get a flashcard set by ID."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard set
            flashcard_set = FlashcardSet.query.filter_by(
                id=set_id,
                session_id=session_id
            ).first()
            
            if not flashcard_set:
                raise ValueError("Flashcard set not found")
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'flashcard_set': flashcard_set.to_dict(include_flashcards=True)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving flashcard set {set_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session_flashcard_sets(self, session_id: str) -> Dict:
        """Get all flashcard sets for a session."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard sets
            flashcard_sets = FlashcardSet.query.filter_by(
                session_id=session_id
            ).order_by(FlashcardSet.created_at.desc()).all()
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'flashcard_sets': [fs.to_dict() for fs in flashcard_sets],
                'count': len(flashcard_sets)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving flashcard sets for session {session_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_flashcard_set(self, set_id: str, session_id: str) -> Dict:
        """Delete a flashcard set."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard set
            flashcard_set = FlashcardSet.query.filter_by(
                id=set_id,
                session_id=session_id
            ).first()
            
            if not flashcard_set:
                raise ValueError("Flashcard set not found")
            
            # Delete flashcard set (cascades to flashcards)
            flashcard_set.delete()
            
            logger.info(f"Deleted flashcard set {set_id}")
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'message': 'Flashcard set deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting flashcard set {set_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_flashcard_set_title(self, set_id: str, session_id: str, new_title: str) -> Dict:
        """Update flashcard set title."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard set
            flashcard_set = FlashcardSet.query.filter_by(
                id=set_id,
                session_id=session_id
            ).first()
            
            if not flashcard_set:
                raise ValueError("Flashcard set not found")
            
            # Update title
            flashcard_set.update(title=new_title.strip())
            
            logger.info(f"Updated flashcard set {set_id} title")
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'flashcard_set': flashcard_set.to_dict(),
                'message': 'Title updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating flashcard set {set_id} title: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def record_study_session(self, set_id: str, session_id: str, cards_studied: List[Dict]) -> Dict:
        """Record a study session with card performance."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard set
            flashcard_set = FlashcardSet.query.filter_by(
                id=set_id,
                session_id=session_id
            ).first()
            
            if not flashcard_set:
                raise ValueError("Flashcard set not found")
            
            # Update individual card statistics
            for card_data in cards_studied:
                card_id = card_data.get('card_id')
                correct = card_data.get('correct', False)
                
                flashcard = Flashcard.query.filter_by(
                    id=card_id,
                    set_id=set_id
                ).first()
                
                if flashcard:
                    flashcard.record_study_attempt(correct=correct)
            
            logger.info(f"Recorded study session for flashcard set {set_id}")
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'message': 'Study session recorded successfully'
            }
            
        except Exception as e:
            logger.error(f"Error recording study session for set {set_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_study_statistics(self, set_id: str, session_id: str) -> Dict:
        """Get study statistics for a flashcard set."""
        
        try:
            # Validate session
            session = Session.get_active_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Get flashcard set
            flashcard_set = FlashcardSet.query.filter_by(
                id=set_id,
                session_id=session_id
            ).first()
            
            if not flashcard_set:
                raise ValueError("Flashcard set not found")
            
            # Calculate statistics
            flashcards = flashcard_set.get_flashcards_ordered()
            total_cards = len(flashcards)
            studied_cards = sum(1 for card in flashcards if card.times_studied > 0)
            total_attempts = sum(card.times_studied for card in flashcards)
            total_correct = sum(card.times_correct for card in flashcards)
            
            overall_success_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
            
            # Card-level statistics
            card_stats = []
            for card in flashcards:
                card_stats.append({
                    'id': card.id,
                    'question': card.question[:50] + '...' if len(card.question) > 50 else card.question,
                    'times_studied': card.times_studied,
                    'success_rate': card.get_success_rate(),
                    'last_studied': card.last_studied.isoformat() if card.last_studied else None
                })
            
            # Update session activity
            session.update_activity()
            
            return {
                'success': True,
                'statistics': {
                    'total_cards': total_cards,
                    'studied_cards': studied_cards,
                    'total_attempts': total_attempts,
                    'overall_success_rate': round(overall_success_rate, 1),
                    'card_statistics': card_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting study statistics for set {set_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }