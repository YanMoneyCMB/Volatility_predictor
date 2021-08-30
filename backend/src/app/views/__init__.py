from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy


class Predict(Resource):
    def get(self, index, period):
        return {index: period}



