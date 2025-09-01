from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows your frontend to make requests to this server

@app.route('/health', methods=['GET'])
def health_check():
    """A simple health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Backend is running!'})

@app.route('/api/process-notes', methods=['POST'])
def process_notes():
    """Processes notes and returns flashcards."""
    data = request.json
    notes = data.get('notes', '')

    if len(notes) < 50:
        return jsonify({'error': 'Notes must be at least 50 characters long'}), 400

    # This is a mock flashcard generation. In a real app, this would
    # be replaced by a call to an AI service like Hugging Face.
    flashcards = []
    # Create simple questions and answers from the notes
    lines = notes.strip().split('\n')
    for i, line in enumerate(lines[:5]): # Limit to 5 flashcards
        question = f"Question {i+1}: What is the main point of this note: '{line.strip()[:30]}...'?"
        answer = f"Answer {i+1}: The note discusses '{line.strip()}'."
        flashcards.append({"question": question, "answer": answer})

    return jsonify({"flashcards": flashcards})

if __name__ == '__main__':
    app.run(debug=True, port=5000)