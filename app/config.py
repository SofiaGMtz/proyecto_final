import os
class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://admin:postgreshola@l172.28.208.1/proyecto'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY','9a4476cae099039918b4dcb7e9f06a52')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM','HS256')