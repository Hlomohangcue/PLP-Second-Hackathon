from .base import db, BaseModel
from datetime import datetime

class FlashcardSet(BaseModel, db.Model):
    """Flashcard set model to group related flashcards."""
    
    __tablename__ = 'flashcard_sets'
    
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    original_content = db.Column(db.Text, nullable=False)
    content_length = db.Column(db.Integer, nullable=False)
    generation_method = db.Column(db.String(50), default='ai', nullable=False)  # 'ai' or 'fallback'
    
    # Relationship with flashcards
    flashcards = db.relationship('Flashcard', backref='flashcard_set', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, session_id, original_content, title=None, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.original_content = original_content
        self.content_length = len(original_content)
        self.title = title or self._generate_title()
    
    def _generate_title(self):
        """Generate a title from the content."""
        words = self.original_content.split()
        if len(words) > 5:
            return ' '.join(words[:5]) + '...'
        return self.original_content[:50] + ('...' if len(self.original_content) > 50 else '')
    
    def add_flashcard(self, question, answer, difficulty='medium', card_order=None):
        """Add a flashcard to this set."""
        if card_order is None:
            card_order = len(self.flashcards) + 1
        
        flashcard = Flashcard(
            set_id=self.id,
            question=question,
            answer=answer,
            difficulty_level=difficulty,
            card_order=card_order
        )
        return flashcard.save()
    
    def get_flashcards_ordered(self):
        """Get flashcards in order."""
        return Flashcard.query.filter_by(set_id=self.id).order_by(Flashcard.card_order).all()
    
    def to_dict(self, include_flashcards=False):
        """Convert flashcard set to dictionary."""
        data = super().to_dict()
        data['flashcard_count'] = len(self.flashcards)
        
        if include_flashcards:
            data['flashcards'] = [card.to_dict() for card in self.get_flashcards_ordered()]
        
        return data
    
    @classmethod
    def create_set_with_flashcards(cls, session_id, original_content, flashcards_data, title=None, generation_method='ai'):
        """Create a flashcard set with flashcards in one transaction."""
        flashcard_set = cls(
            session_id=session_id,
            original_content=original_content,
            title=title,
            generation_method=generation_method
        ).save()
        
        for i, card_data in enumerate(flashcards_data):
            flashcard_set.add_flashcard(
                question=card_data['question'],
                answer=card_data['answer'],
                difficulty=card_data.get('difficulty', 'medium'),
                card_order=i + 1
            )
        
        return flashcard_set

class Flashcard(BaseModel, db.Model):
    """Individual flashcard model."""
    
    __tablename__ = 'flashcards'
    
    set_id = db.Column(db.String(36), db.ForeignKey('flashcard_sets.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    card_order = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard', name='difficulty_levels'), 
                                default='medium', nullable=False)
    
    # Study tracking fields (for future analytics)
    times_studied = db.Column(db.Integer, default=0, nullable=False)
    times_correct = db.Column(db.Integer, default=0, nullable=False)
    last_studied = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, set_id, question, answer, card_order, difficulty_level='medium', **kwargs):
        super().__init__(**kwargs)
        self.set_id = set_id
        self.question = question.strip()
        self.answer = answer.strip()
        self.card_order = card_order
        self.difficulty_level = difficulty_level
    
    def record_study_attempt(self, correct=False):
        """Record a study attempt."""
        self.times_studied += 1
        if correct:
            self.times_correct += 1
        self.last_studied = datetime.utcnow()
        db.session.commit()
    
    def get_success_rate(self):
        """Get the success rate for this card."""
        if self.times_studied == 0:
            return 0
        return (self.times_correct / self.times_studied) * 100
    
    def to_dict(self):
        """Convert flashcard to dictionary."""
        data = super().to_dict()
        data['success_rate'] = self.get_success_rate()
        return data
    
    @classmethod
    def get_by_set(cls, set_id, ordered=True):
        """Get all flashcards for a set."""
        query = cls.query.filter_by(set_id=set_id)
        if ordered:
            query = query.order_by(cls.card_order)
        return query.all()