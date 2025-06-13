from flask import Flask, request, jsonify, send_file
from logger.logger import Logger
from routes.route import FileGeneratorRoute  
from schemas.schemaPDF import CrearPDF
from services.service import Service
from models.model import BDModel

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

logger = Logger()

#ESQUEMA NUEVO
form_schema = CrearPDF()

# Model
db_conn = BDModel()
db_conn.connect_to_database()

# Service
service = Service(db_conn)

# Routes
form_routes = FileGeneratorRoute(service, form_schema)

#Blueprint
app.register_blueprint(form_routes)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", debug=False)
        logger.info("Application started")
    finally:
        db_conn.close_connection()
        logger.info("Application closed")
        logger.info("MongoDB connection closed")