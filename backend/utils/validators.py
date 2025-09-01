import re
from typing import Dict, Union

class ContentValidator:
    """Validator for user input content."""
    
    def __init__(self, min_length: int = 50, max_length: int = 2000):
        self.min_length = min_length
        self.max_length = max_length

    def validate_content(self, content: str) -> Dict[str, Union[bool, str]]:
        """Validate study notes content."""
        
        if not content or not isinstance(content, str):
            return {
                'valid': False,
                'error': 'Content is required and must be text'
            }
        
        # Clean whitespace
        content = content.strip()
        
        if len(content) < self.min_length:
            return {
                'valid': False,
                'error': f'Content must be at least {self.min_length} characters long'
            }
        
        if len(content) > self.max_length:
            return {
                'valid': False,
                'error': f'Content cannot exceed {self.max_length} characters'
            }
        
        # Check for meaningful content (not just repeated characters)
        if self._is_low_quality_content(content):
            return {
                'valid': False,
                'error': 'Please provide meaningful study content with varied text'
            }
        
        return {
            'valid': True,
            'cleaned_content': content
        }
    
    def _is_low_quality_content(self, content: str) -> bool:
        """Check if content appears to be low quality."""
        
        # Check for repeated characters
        if len(set(content.lower())) < 10:
            return True
        
        # Check for repeated words (more than 50% repetition)
        words = content.lower().split()
        if len(words) > 10:
            unique_words = set(words)
            repetition_ratio = len(words) / len(unique_words)
            if repetition_ratio > 2.0:
                return True
        
        # Check for minimal sentences
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) < 2:
            return True
        
        return False
    
    def validate_session_id(self, session_id: str) -> Dict[str, Union[bool, str]]:
        """Validate session ID format."""
        
        if not session_id or not isinstance(session_id, str):
            return {
                'valid': False,
                'error': 'Session ID is required'
            }
        
        # UUID format validation
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_pattern.match(session_id):
            return {
                'valid': False,
                'error': 'Invalid session ID format'
            }
        
        return {'valid': True}
    
    def validate_title(self, title: str) -> Dict[str, Union[bool, str]]:
        """Validate flashcard set title."""
        
        if not title:
            return {'valid': True}  # Title is optional
        
        if not isinstance(title, str):
            return {
                'valid': False,
                'error': 'Title must be text'
            }
        
        title = title.strip()
        
        if len(title) > 255:
            return {
                'valid': False,
                'error': 'Title cannot exceed 255 characters'
            }
        
        if len(title) < 3:
            return {
                'valid': False,
                'error': 'Title must be at least 3 characters long'
            }
        
        return {
            'valid': True,
            'cleaned_title': title
        }
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent XSS and other issues."""
        
        if not isinstance(text, str):
            return ''
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
