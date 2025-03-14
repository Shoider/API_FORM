from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import pandas as pd
from fpdf import FPDF
from logger.logger import Logger
from schemas.schema import RegistroSchema 
from routes.route import FileGeneratorRoute  
from marshmallow import ValidationError
import os

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

logger = Logger()

# Schema
form_schema = RegistroSchema()

# Routes
form_routes = FileGeneratorRoute(form_schema)

#Blueprint
app.register_blueprint(form_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)