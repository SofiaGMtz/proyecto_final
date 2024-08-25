from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship
from .answers import Answer
from .votes import Vote

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='questions')
    answers = db.relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.title}>'

    def count_answers(self):
        return len(self.answers)

    def count_likes(self):
        return Vote.query.join(Answer).filter(
            Answer.question_id == self.id,
            Vote.is_upvote == True
        ).count()

    def save(self):
        db.session.add(self)
        db.session.commit()