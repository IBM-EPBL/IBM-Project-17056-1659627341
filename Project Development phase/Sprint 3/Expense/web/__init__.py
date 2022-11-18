from flask import Flask
from .connect import get_db_connection
from .auth import auth
from .feature import feature

con = 0
def createApp():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = "abcdef"

    con = get_db_connection()

    app.register_blueprint(auth)
    app.register_blueprint(feature)

    return app