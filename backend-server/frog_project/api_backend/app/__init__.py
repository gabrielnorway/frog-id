from flask import Flask
from .secrets import Secrets
from .db_connector import db_uri
from flask_login import LoginManager
from .exts import db, scheduler
from .classes import User, Frog, Image

UPLOAD_FOLDER = '/frog_images/unknown/'
FROG_IMAGE_FOLDER = '/frog_images/identified/'

def create_app(environ=None, start_response=None):
    flask_app = Flask(__name__)
    flask_app.config['SECRET_KEY'] = Secrets.app_secret_key
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    flask_app.config['FROG_IMAGE_FOLDER'] = FROG_IMAGE_FOLDER

    db.init_app(flask_app)
    scheduler.init_app(flask_app)
    scheduler.start()

    from .app import app as app_blueprint
    flask_app.register_blueprint(app_blueprint)

    # user authentication
    from .authentication import authentication as auth_blueprint
    flask_app.register_blueprint(auth_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'authentication.login'
    login_manager.init_app(flask_app)

    @login_manager.user_loader
    def user_loader(user_id):
        with flask_app.app_context():
            return User.query.get(int(user_id))

    return flask_app


