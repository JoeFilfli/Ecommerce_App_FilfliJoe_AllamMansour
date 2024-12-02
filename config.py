class Config:
    SECRET_KEY = 'supersecret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///customers.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'randomstring'
    JWT_ALGORITHM = 'HS256'