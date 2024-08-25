rom app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), nullable=False)
  password = db.Column(db.Text(), nullable=False)

  questions = db.relationship('Question', back_populates='user')
  answers = db.relationship('Answer', back_populates='user')

  def __repr__(self):
    return f'<Usuario es {self.username}>'

  def set_password(self, password):
    self.password = generate_password_hash(password)
  
  def check_password(self, password):
    return check_password_hash(self.password, password)

  @classmethod
  def get_user_by_email(cls, email):
    return cls.query.filter_by(email=email).first()

  def save(self):
    db.session.add(self)
    db.session.commit()  

  def delete(self):
    db.session.delete(self)
    db.session.commit()