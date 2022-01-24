import os 
from flask import Flask
from myapp.auth.auth import auth
from myapp.views.home import main
from myapp.views.posts import posts
from flask_login import LoginManager
from flask import send_from_directory
from myapp.model.db_extension import db
from myapp.model.ma_extension import ma
from myapp.model.model import User
from myapp.model.post_model import Posts
from myapp.views.pdf_file import pdf
from flask_ldap3_login import LDAP3LoginManager


def create_app(test_config='config'):
    app = Flask(__name__, instance_relative_config=True)

    # app.config.from_object('config')
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_object(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(main)
    # app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(posts)
    app.register_blueprint(pdf)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    ldap_manager = LDAP3LoginManager() 
    
    login_manager.init_app(app)

    db.init_app(app)
    ma.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    @app.route('/favicon.ico') 
    def favicon(): 
        return send_from_directory(os.path.join(app.root_path, 'static\\assets'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app