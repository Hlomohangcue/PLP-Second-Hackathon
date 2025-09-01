import os
import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///flashcards.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

# Hugging Face API configuration
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")

# Models to try (in order of preference)
AVAILABLE_MODELS = [
    "https://api-inference.huggingface.co/models/gpt2",
    "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
    "https://api-inference.huggingface.co/models/distilbert-base-cased-distilled-squad",
    "https://api-inference.huggingface.co/models/google/flan-t5-small"
]

# --- Database Models ---
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Flashcard {self.id}>'

# --- AI Service Functions ---
def generate_flashcards_from_notes(notes):
    """Generate flashcards from notes using Hugging Face API or fallback"""
    
    if not HUGGING_FACE_API_TOKEN:
        print("Error: Hugging Face API token is not set.")
        return generate_smart_fallback_flashcards(notes)

    print("Attempting to use AI models for flashcard generation...")
    
    # Try available models
    for model_url in AVAILABLE_MODELS:
        print(f"Trying model: {model_url}")
        result = try_model_for_flashcards(model_url, notes)
        if result and len(result) >= 2:
            print(f"Success with model: {model_url}")
            return result
    
    print("All AI models failed, using intelligent fallback generation")
    return generate_smart_fallback_flashcards(notes)

def try_model_for_flashcards(model_url, notes):
    """Try a specific model for generating flashcards"""
    
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Different prompts for different model types
    if "bart" in model_url.lower():
        payload = {
            "inputs": notes[:500],
            "parameters": {
                "max_length": 100,
                "min_length": 30
            }
        }
    elif "distilbert" in model_url.lower() and "squad" in model_url.lower():
        return try_qa_model(model_url, notes, headers)
    elif "flan-t5" in model_url.lower():
        prompt = f"Generate 3 study questions from this text: {notes[:300]}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
    else:
        prompt = f"Create study questions from this text:\n{notes[:400]}\n\nQ:"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.8,
                "return_full_text": False
            }
        }

    try:
        response = requests.post(model_url, headers=headers, json=payload, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Model failed with status {response.status_code}: {response.text[:200]}")
            return None
        
        response_data = response.json()
        print(f"Response type: {type(response_data)}")
        
        if isinstance(response_data, list) and len(response_data) > 0:
            first_result = response_data[0]
            
            if 'generated_text' in first_result:
                generated_text = first_result['generated_text']
                return parse_generated_flashcards(generated_text, notes)
            elif 'summary_text' in first_result:
                summary = first_result['summary_text']
                return create_flashcards_from_summary(summary, notes)
            else:
                print(f"Unknown response format: {first_result}")
                return None
        else:
            print(f"Unexpected response format: {response_data}")
            return None
        
    except Exception as e:
        print(f"Error with model {model_url}: {e}")
        return None

def try_qa_model(model_url, notes, headers):
    """Try Q&A model with predefined questions"""
    questions = [
        "What is the main topic?",
        "What are the key concepts?",
        "What should I remember?",
        "How does this work?",
        "What are the important details?"
    ]
    
    flashcards = []
    for question in questions[:3]:
        payload = {
            "inputs": {
                "question": question,
                "context": notes[:400]
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
                        "answer": answer
                    })
        except Exception as e:
            print(f"Q&A model error: {e}")
            continue
    
    return flashcards if len(flashcards) >= 2 else None

def parse_generated_flashcards(generated_text, original_notes):
    """Parse flashcards from generated text with better logic"""
    flashcards = []
    
    text = generated_text.lower()
    
    if 'q:' in text and 'a:' in text:
        parts = generated_text.split('Q: ')[1:]
        for part in parts:
            if 'A: ' in part:
                try:
                    question_part, answer_part = part.split('A: ', 1)
                    question = question_part.strip().rstrip('?').strip()
                    answer = answer_part.split('Q: ')[0].strip()
                    
                    if question and answer and len(question) > 5 and len(answer) > 5:
                        flashcards.append({
                            "question": question,
                            "answer": answer
                        })
                except:
                    continue
    
    if len(flashcards) < 2:
        sentences = [s.strip() for s in generated_text.split('.') if '?' in s]
        for sentence in sentences[:3]:
            if len(sentence) > 20:
                question = sentence.strip()
                answer = original_notes[:100] + "..." if len(original_notes) > 100 else original_notes
                flashcards.append({
                    "question": question,
                    "answer": answer
                })
    
    return flashcards[:5]

def create_flashcards_from_summary(summary, original_notes):
    """Create flashcards when we get a summary instead of Q&A format"""
    print(f"Creating flashcards from summary: {summary[:100]}...")
    
    flashcards = []
    
    if "programming" in summary.lower():
        flashcards.append({
            "question": "What is the main subject of these notes?",
            "answer": summary.strip()
        })
    
    sentences = [s.strip() for s in summary.split('.') if len(s.strip()) > 15]
    
    for i, sentence in enumerate(sentences[:3]):
        if len(sentence) > 20:
            flashcards.append({
                "question": "What key point is mentioned about the topic?",
                "answer": sentence.strip()
            })
    
    if len(flashcards) < 3:
        return generate_smart_fallback_flashcards(original_notes)
    
    return flashcards[:5]

def generate_smart_fallback_flashcards(notes):
    """Generate intelligent flashcards based on content analysis"""
    print("Using smart fallback flashcard generation...")
    
    flashcards = []
    notes_lower = notes.lower()
    sentences = [s.strip() for s in notes.split('.') if len(s.strip()) > 20]
    
    # Programming-specific patterns
    if any(word in notes_lower for word in ['programming', 'code', 'coding', 'software']):
        flashcards.append({
            "question": "What is the main topic of these notes?",
            "answer": "Programming and software development"
        })
        
        # Look for programming languages
        languages = []
        for lang in ['python', 'javascript', 'java', 'c++', 'html', 'css', 'sql', 'php']:
            if lang in notes_lower:
                languages.append(lang.capitalize())
        
        if languages:
            flashcards.append({
                "question": "What programming languages are mentioned?",
                "answer": ", ".join(languages)
            })
        
        # Look for programming concepts
        concepts = []
        for concept in ['algorithm', 'variable', 'function', 'loop', 'array', 'object', 'class']:
            if concept in notes_lower:
                concepts.append(concept)
        
        if concepts:
            flashcards.append({
                "question": "What programming concepts are discussed?",
                "answer": ", ".join(concepts).title()
            })
    
    # Look for definitions
    for sentence in sentences:
        if any(word in sentence.lower() for word in [' is ', ' are ', ' means ', ' refers to ']):
            if len(flashcards) < 5:
                words = sentence.split()
                subject = " ".join(words[:3])
                flashcards.append({
                    "question": f"What is {subject}?",
                    "answer": sentence.strip()
                })
    
    # Look for processes
    action_words = ['create', 'build', 'develop', 'design', 'implement', 'use', 'apply']
    for sentence in sentences:
        if any(action in sentence.lower() for action in action_words) and len(flashcards) < 5:
            flashcards.append({
                "question": "What process is described in the notes?",
                "answer": sentence.strip()
            })
    
    # Look for benefits or advantages
    for sentence in sentences:
        if any(word in sentence.lower() for word in ['benefit', 'advantage', 'important', 'essential', 'useful']):
            if len(flashcards) < 5:
                flashcards.append({
                    "question": "What are the benefits or important points mentioned?",
                    "answer": sentence.strip()
                })
    
    # Ensure we have at least 3 flashcards
    while len(flashcards) < 3:
        if len(sentences) > len(flashcards):
            sentence = sentences[len(flashcards)]
            flashcards.append({
                "question": "What key information is provided in the notes?",
                "answer": sentence
            })
        else:
            flashcards.append({
                "question": "What should you remember from these study notes?",
                "answer": notes[:150] + "..." if len(notes) > 150 else notes
            })
    
    return flashcards[:5]

# --- API Routes ---
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AI Study Buddy backend!", "status": "running"})

@app.route('/api/process-notes', methods=['POST'])
def process_notes():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        notes = data.get('notes', '')

        if not notes or len(notes.strip()) < 50:
            return jsonify({"error": "Notes must be at least 50 characters long"}), 400

        print(f"Processing notes of length: {len(notes)}")
        flashcards_data = generate_flashcards_from_notes(notes)
        
        if not flashcards_data:
            return jsonify({"error": "Failed to generate flashcards. Please try again with different content."}), 500
            
        try:
            for card_data in flashcards_data:
                new_flashcard = Flashcard(
                    question=card_data['question'],
                    answer=card_data['answer']
                )
                db.session.add(new_flashcard)
            db.session.commit()
            print(f"Saved {len(flashcards_data)} flashcards to database")
        except Exception as e:
            db.session.rollback()
            print(f"Database save error: {e}")
            return jsonify({"error": "Failed to save flashcards to the database."}), 500
            
        return jsonify({
            "message": "Flashcards generated and saved successfully!", 
            "flashcards": flashcards_data,
            "count": len(flashcards_data)
        })
        
    except Exception as e:
        print(f"Unexpected error in process_notes: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    """Get all saved flashcards"""
    try:
        flashcards = Flashcard.query.all()
        flashcards_data = [
            {
                "id": card.id,
                "question": card.question,
                "answer": card.answer,
                "created_at": card.created_at.isoformat()
            }
            for card in flashcards
        ]
        return jsonify({"flashcards": flashcards_data, "count": len(flashcards_data)})
    except Exception as e:
        print(f"Error fetching flashcards: {e}")
        return jsonify({"error": "Failed to fetch flashcards"}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "hugging_face_token_set": bool(HUGGING_FACE_API_TOKEN),
        "database_url": app.config['SQLALCHEMY_DATABASE_URI']
    })

# --- Main Entry Point ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    print(f"Starting app with HF token: {'SET' if HUGGING_FACE_API_TOKEN else 'NOT SET'}")
    app.run(debug=True, host='0.0.0.0', port=5000)