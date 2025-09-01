from datetime import datetime, timedelta
from .base import db, BaseModel

class Session(BaseModel, db.Model):
    """User session model for tracking anonymous users."""
    
    __tablename__ = 'sessions'
    
    last_active = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship with flashcard sets
    flashcard_sets = db.relationship('FlashcardSet', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, timeout_days=30, **kwargs):
        super().__init__(**kwargs)
        self.expires_at = datetime.utcnow() + timedelta(days=timeout_days)
    
    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Update last_active timestamp."""
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    def extend_session(self, days=30):
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def create_session(cls, timeout_days=30):
        """Create a new session."""
        session = cls(timeout_days=timeout_days)
        return session.save()
    
    @classmethod
    def get_active_session(cls, session_id):
        """Get active session by ID."""
        session = cls.query.filter_by(id=session_id, is_active=True).first()
        if session and not session.is_expired():
            session.update_activity()
            return session
        elif session:
            session.deactivate()
        return None
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Remove expired sessions from database."""
        expired_sessions = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return len(expired_sessions)
    
    def to_dict(self):
        """Convert session to dictionary."""
        data = super().to_dict()
        data['flashcard_sets_count'] = len(self.flashcard_sets)
        data['is_expired'] = self.is_expired()
        return data