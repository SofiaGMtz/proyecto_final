from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import relationship

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    is_upvote = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    answer = db.relationship('Answer', backref=db.backref('votes', lazy=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete_vote(self):
        db.session.delete(self)
        db.session.commit()