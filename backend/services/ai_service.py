import requests
import logging
import re
from typing import List, Dict, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered flashcard generation using Hugging Face API."""
    
    def __init__(self):
        self.api_token = current_app.config.get('HUGGING_FACE_API_TOKEN')
        self.available_models = current_app.config.get('AVAILABLE_MODELS', [])
        self.timeout = 30
    
    def generate_flashcards(self, content: str, count: int = 5) -> List[Dict[str, str]]:
        """Generate flashcards from content using AI or fallback methods."""
        
        if not self.api_token:
            logger.warning("Hugging Face API token not set, using fallback generation")
            return self._generate_fallback_flashcards(content, count)
        
        logger.info(f"Attempting AI flashcard generation for {len(content)} characters")
        
        # Try each available model
        for model_url in self.available_models:
            try:
                result = self._try_model(model_url, content, count)
                if result and len(result) >= 2:
                    logger.info(f"Successfully generated {len(result)} flashcards using {model_url}")
                    return result[:count]
            except Exception as e:
                logger.error(f"Model {model_url} failed: {str(e)}")
                continue
        
        logger.warning("All AI models failed, using fallback generation")
        return self._generate_fallback_flashcards(content, count)
    
    def _try_model(self, model_url: str, content: str, count: int) -> Optional[List[Dict[str, str]]]:
        """Try a specific model for generating flashcards."""
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Choose strategy based on model type
        if "bart" in model_url.lower():
            return self._try_bart_model(model_url, headers, content, count)
        elif "distilbert" in model_url.lower() and "squad" in model_url.lower():
            return self._try_qa_model(model_url, headers, content, count)
        elif "flan-t5" in model_url.lower():
            return self._try_flan_model(model_url, headers, content, count)
        else:
            return self._try_gpt_model(model_url, headers, content, count)
    
    def _try_bart_model(self, model_url: str, headers: dict, content: str, count: int) -> Optional[List[Dict[str, str]]]:
        """Try BART model for summarization-based flashcard generation."""
        
        payload = {
            "inputs": content[:500],  # BART has token limits
            "parameters": {
                "max_length": 150,
                "min_length": 30,
                "do_sample": True,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'summary_text' in data[0]:
                    summary = data[0]['summary_text']
                    return self._create_flashcards_from_summary(summary, content, count)
        except Exception as e:
            logger.error(f"BART model error: {e}")
        
        return None
    
    def _try_qa_model(self, model_url: str, headers: dict, content: str, count: int) -> Optional[List[Dict[str, str]]]:
        """Try Q&A model with predefined questions."""
        
        questions = [
            "What is the main topic discussed?",
            "What are the key concepts mentioned?",
            "What should someone remember from this?",
            "How does this process work?",
            "What are the important details?",
            "What is the significance of this information?",
            "What are the main points covered?"
        ]
        
        flashcards = []
        for question in questions[:count]:
            payload = {
                "inputs": {
                    "question": question,
                    "context": content[:400]  # Context length limit
                }
            }
            
            try:
                response = requests.post(model_url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '').strip()
                    if answer and len(answer) > 10:
                        flashcards.append({
                            "question": question,
                            "answer": answer,
                            "difficulty": "medium"
                        })
            except Exception as e:
                logger.error(f"Q&A model error for question '{question}': {e}")
                continue
        
        return flashcards if len(flashcards) >= 2 else None
    
    def _try_flan_model(self, model_url: str, headers: dict, content: str, count: int) -> Optional[List[Dict[str, str]]]:
        """Try FLAN-T5 model for question generation."""
        
        prompt = f"""Based on this text, create {count} study questions with answers:

{content[:300]}

Format your response as:
Q: [question]
A: [answer]
Q: [question]
A: [answer]"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
                    generated_text = data[0]['generated_text']
                    return self._parse_qa_format(generated_text)
        except Exception as e:
            logger.error(f"FLAN model error: {e}")
        
        return None
    
    def _try_gpt_model(self, model_url: str, headers: dict, content: str, count: int) -> Optional[List[Dict[str, str]]]:
        """Try GPT-style model for question generation."""
        
        prompt = f"Create {count} study questions from this text:\n\n{content[:400]}\n\nQ:"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.8,
                "return_full_text": False,
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
                    generated_text = data[0]['generated_text']
                    return self._parse_generated_text(generated_text, content)
        except Exception as e:
            logger.error(f"GPT model error: {e}")
        
        return None
    
    def _parse_qa_format(self, text: str) -> List[Dict[str, str]]:
        """Parse Q: A: formatted text into flashcards."""
        
        flashcards = []
        # Split by Q: and process each section
        sections = re.split(r'Q:\s*', text, flags=re.IGNORECASE)[1:]  # Skip first empty split
        
        for section in sections:
            if 'A:' in section or 'a:' in section:
                # Split on A: (case insensitive)
                parts = re.split(r'A:\s*', section, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    question = parts[0].strip().rstrip('?').strip()
                    answer_part = parts[1].strip()
                    # Remove next Q: if present
                    answer = re.split(r'Q:\s*', answer_part, flags=re.IGNORECASE)[0].strip()
                    
                    if len(question) > 10 and len(answer) > 10:
                        flashcards.append({
                            "question": question + "?" if not question.endswith('?') else question,
                            "answer": answer,
                            "difficulty": "medium"
                        })
        
        return flashcards[:5]
    
    def _parse_generated_text(self, generated_text: str, original_content: str) -> List[Dict[str, str]]:
        """Parse various formats of generated text."""
        
        # Try Q:/A: format first
        flashcards = self._parse_qa_format(generated_text)
        if flashcards:
            return flashcards
        
        # Try to find question sentences
        sentences = [s.strip() for s in generated_text.split('.') if '?' in s and len(s.strip()) > 15]
        flashcards = []
        
        for sentence in sentences[:3]:
            if len(sentence) > 20:
                question = sentence.strip()
                # Generate answer from original content
                answer = self._extract_relevant_answer(question, original_content)
                flashcards.append({
                    "question": question,
                    "answer": answer,
                    "difficulty": "medium"
                })
        
        return flashcards
    
    def _create_flashcards_from_summary(self, summary: str, original_content: str, count: int) -> List[Dict[str, str]]:
        """Create flashcards when we get a summary instead of Q&A format."""
        
        flashcards = []
        
        # Create a general question about the content
        flashcards.append({
            "question": "What is the main topic of these notes?",
            "answer": summary.strip(),
            "difficulty": "easy"
        })
        
        # Break summary into key points
        sentences = [s.strip() for s in summary.split('.') if len(s.strip()) > 20]
        
        for i, sentence in enumerate(sentences[:count-1]):
            if len(sentence) > 25:
                flashcards.append({
                    "question": f"What key point is mentioned about the topic?",
                    "answer": sentence.strip(),
                    "difficulty": "medium"
                })
        
        return flashcards[:count]
    
    def _generate_fallback_flashcards(self, content: str, count: int = 5) -> List[Dict[str, str]]:
        """Generate intelligent fallback flashcards based on content analysis."""
        
        logger.info("Using intelligent fallback flashcard generation")
        
        flashcards = []
        content_lower = content.lower()
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        # Detect content type and create appropriate questions
        if self._is_programming_content(content_lower):
            flashcards.extend(self._generate_programming_flashcards(content, sentences))
        elif self._is_science_content(content_lower):
            flashcards.extend(self._generate_science_flashcards(content, sentences))
        elif self._is_history_content(content_lower):
            flashcards.extend(self._generate_history_flashcards(content, sentences))
        else:
            flashcards.extend(self._generate_general_flashcards(content, sentences))
        
        # Ensure we have enough flashcards
        while len(flashcards) < count and len(sentences) > len(flashcards):
            sentence = sentences[len(flashcards)]
            flashcards.append({
                "question": "What key information is provided in the notes?",
                "answer": sentence,
                "difficulty": "medium"
            })
        
        return flashcards[:count]
    
    def _is_programming_content(self, content: str) -> bool:
        """Check if content is programming-related."""
        programming_keywords = [
            'programming', 'code', 'coding', 'software', 'python', 'javascript', 
            'java', 'html', 'css', 'algorithm', 'function', 'variable', 'array',
            'object', 'class', 'method', 'api', 'database', 'framework'
        ]
        return any(keyword in content for keyword in programming_keywords)
    
    def _is_science_content(self, content: str) -> bool:
        """Check if content is science-related."""
        science_keywords = [
            'experiment', 'hypothesis', 'theory', 'research', 'study', 'analysis',
            'biology', 'chemistry', 'physics', 'molecule', 'cell', 'organism',
            'equation', 'formula', 'reaction', 'energy', 'matter'
        ]
        return any(keyword in content for keyword in science_keywords)
    
    def _is_history_content(self, content: str) -> bool:
        """Check if content is history-related."""
        history_keywords = [
            'century', 'year', 'war', 'battle', 'empire', 'king', 'queen',
            'revolution', 'ancient', 'medieval', 'modern', 'civilization',
            'culture', 'society', 'political', 'economic'
        ]
        return any(keyword in content for keyword in history_keywords)
    
    def _generate_programming_flashcards(self, content: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate programming-specific flashcards."""
        flashcards = []
        content_lower = content.lower()
        
        # Language detection
        languages = []
        for lang in ['python', 'javascript', 'java', 'c++', 'html', 'css', 'sql', 'php', 'react', 'flask']:
            if lang in content_lower:
                languages.append(lang.title())
        
        if languages:
            flashcards.append({
                "question": "What programming languages or technologies are mentioned?",
                "answer": ", ".join(languages),
                "difficulty": "easy"
            })
        
        # Concept detection
        concepts = []
        for concept in ['algorithm', 'variable', 'function', 'loop', 'array', 'object', 'class', 'method']:
            if concept in content_lower:
                concepts.append(concept)
        
        if concepts:
            flashcards.append({
                "question": "What programming concepts are discussed?",
                "answer": ", ".join(concepts).title(),
                "difficulty": "medium"
            })
        
        return flashcards
    
    def _generate_science_flashcards(self, content: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate science-specific flashcards."""
        flashcards = []
        
        # Look for definitions and processes
        for sentence in sentences[:3]:
            if any(word in sentence.lower() for word in [' is ', ' are ', ' occurs ', ' happens']):
                flashcards.append({
                    "question": "What scientific concept or process is described?",
                    "answer": sentence,
                    "difficulty": "medium"
                })
                break
        
        return flashcards
    
    def _generate_history_flashcards(self, content: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate history-specific flashcards."""
        flashcards = []
        
        # Look for dates and events
        import re
        dates = re.findall(r'\b\d{4}\b', content)  # Find years
        if dates:
            flashcards.append({
                "question": "What years or time periods are mentioned?",
                "answer": ", ".join(set(dates)),
                "difficulty": "easy"
            })
        
        # Look for historical figures or places
        for sentence in sentences[:2]:
            if any(word in sentence.lower() for word in ['king', 'queen', 'president', 'emperor', 'leader']):
                flashcards.append({
                    "question": "What historical figures are mentioned?",
                    "answer": sentence,
                    "difficulty": "medium"
                })
                break
        
        return flashcards
    
    def _generate_general_flashcards(self, content: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Generate general flashcards for any content type."""
        flashcards = []
        
        # Main topic question
        flashcards.append({
            "question": "What is the main topic of these notes?",
            "answer": sentences[0] if sentences else content[:100] + "...",
            "difficulty": "easy"
        })
        
        # Look for definitions
        for sentence in sentences:
            if any(word in sentence.lower() for word in [' is ', ' are ', ' means ', ' refers to ']):
                # Extract the subject being defined
                words = sentence.split()[:5]
                subject = " ".join(words)
                flashcards.append({
                    "question": f"What is {subject.lower()}?",
                    "answer": sentence,
                    "difficulty": "medium"
                })
                break
        
        # Look for processes or methods
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['how to', 'process', 'method', 'steps', 'procedure']):
                flashcards.append({
                    "question": "What process or method is described?",
                    "answer": sentence,
                    "difficulty": "medium"
                })
                break
        
        # Look for benefits or importance
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['important', 'benefit', 'advantage', 'essential', 'crucial']):
                flashcards.append({
                    "question": "What important points or benefits are mentioned?",
                    "answer": sentence,
                    "difficulty": "medium"
                })
                break
        
        return flashcards
    
    def _extract_relevant_answer(self, question: str, content: str) -> str:
        """Extract relevant answer from content based on question."""
        
        # Simple keyword matching to find relevant content
        question_words = question.lower().split()
        content_sentences = content.split('.')
        
        best_sentence = content_sentences[0]  # Default to first sentence
        max_matches = 0
        
        for sentence in content_sentences:
            if len(sentence.strip()) < 20:
                continue
                
            sentence_words = sentence.lower().split()
            matches = sum(1 for word in question_words if word in sentence_words)
            
            if matches > max_matches:
                max_matches = matches
                best_sentence = sentence
        
        return best_sentence.strip()
    
    def validate_flashcards(self, flashcards: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate and clean generated flashcards."""
        
        validated = []
        for card in flashcards:
            # Check required fields
            if not all(key in card for key in ['question', 'answer']):
                continue
            
            question = card['question'].strip()
            answer = card['answer'].strip()
            
            # Validate content quality
            if len(question) < 10 or len(answer) < 10:
                continue
            
            # Ensure question ends with question mark
            if not question.endswith('?'):
                question += '?'
            
            # Clean up formatting
            question = ' '.join(question.split())  # Remove extra whitespace
            answer = ' '.join(answer.split())
            
            validated.append({
                'question': question,
                'answer': answer,
                'difficulty': card.get('difficulty', 'medium')
            })
        
        return validated