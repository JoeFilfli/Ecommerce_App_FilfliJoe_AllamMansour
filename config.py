# Config.py
    
class Config:
    """
    Configuration class for the Flask application.

    Attributes:
        SECRET_KEY (str): Secret key for securing sessions and tokens.
        SQLALCHEMY_DATABASE_URI (str): Database URI for SQLAlchemy.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable SQLAlchemy event system.
        JWT_SECRET_KEY (str): Secret key for encoding JWT tokens.
        JWT_ALGORITHM (str): Algorithm used for JWT token encoding.
    """

    SECRET_KEY = 'supersecret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///customers.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'randomstring'
    JWT_ALGORITHM = 'HS256'
