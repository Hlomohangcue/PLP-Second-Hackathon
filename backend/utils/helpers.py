import uuid
import re
from typing import Dict, Any
from datetime import datetime
from flask import jsonify

def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def sanitize_input(text: str) -> str:
    """Sanitize user input for security."""
    if not isinstance(text, str):
        return ''
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def format_response(success: bool, data: Any = None, error: str = None, message: str = None) -> Dict:
    """Format consistent API responses."""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if success:
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
    else:
        response['error'] = error or 'An error occurred'
    
    return response

def create_json_response(success: bool, data: Any = None, error: str = None, 
                        message: str = None, status_code: int = None):
    """Create a Flask JSON response with consistent format."""
    response_data = format_response(success, data, error, message)
    
    if status_code is None:
        status_code = 200 if success else 400
    
    return jsonify(response_data), status_code

def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract keywords from text for search/tagging purposes."""
    # Simple keyword extraction (can be enhanced with NLP libraries)
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that',
        'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
        'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
        'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
        'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'am', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can'
    }
    
    # Clean and tokenize
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter out stop words and get word frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    return reading_time

def clean_filename(filename: str) -> str:
    """Clean filename for safe filesystem storage."""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores and spaces
    filename = filename.strip('_ ')
    # Ensure it's not empty
    if not filename:
        filename = 'untitled'
    
    return filename

def validate_email(email: str) -> bool:
    """Validate email format (for future user accounts)."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.match(pattern, email) is not None

def format_timestamp(timestamp, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format timestamp for display."""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_str)
    
    return str(timestamp)

def get_content_stats(content: str) -> Dict[str, Any]:
    """Get statistics about content."""
    words = content.split()
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    return {
        'character_count': len(content),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'paragraph_count': len(paragraphs),
        'average_words_per_sentence': round(len(words) / max(1, len(sentences)), 1),
        'reading_time_minutes': calculate_reading_time(content)
    }