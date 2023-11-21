from flask import Flask
from flask_pymongo import PyMongo


def carrental():
    app = Flask(__name__, template_folder="views", static_folder="assets")
    app.config.from_pyfile("../config.py")


    from .views import views
    from .auth import auth


    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth,url_prefix='/')


    return app