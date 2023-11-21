from flask import Flask
from flask_pymongo import PyMongo

db = PyMongo()


def carrental():
    app = Flask(__name__, template_folder="views", static_folder="assets")
    app.config.from_pyfile("../config.py")
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")

    return app
