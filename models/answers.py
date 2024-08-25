from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship
from .votes import Vote

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    question = db.relationship('Question', back_populates='answers')
    user = db.relationship('User', back_populates='answers')

    def upvote_count(self):
        return Vote.query.filter_by(answer_id=self.id, is_upvote=True).count()

    def downvote_count(self):
        return Vote.query.filter_by(answer_id=self.id, is_upvote=False).count()

    def save(self):
        db.session.add(self)
        db.session.commit()