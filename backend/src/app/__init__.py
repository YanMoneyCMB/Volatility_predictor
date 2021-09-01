from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from app.views import Predict,Project






def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Predict, "/Predict/<string:index>/<int:period>")
    api.add_resource(Project,"/Project/<string:index>/<int:period>/<float:prediction>")
    return app

