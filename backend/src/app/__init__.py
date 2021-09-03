from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from app.views import Predict,Project,Options,Tune
from flask_cors import CORS





def create_app():
    app = Flask(__name__)
    CORS(app)
    api = Api(app)
    api.add_resource(Predict, "/Predict/<string:index>/<int:period>")
    api.add_resource(Project,"/Project/<string:index>/<int:period>/<float:prediction>")
    api.add_resource(Options, "/Options/<string:index>/<int:period>")
    api.add_resource(Tune, "/Tune")
    return app
