from flask import Flask, request, jsonify, send_file
from logger.logger import Logger
from schemas.schemaVPN import RegistroSchemaVPN
from schemas.schemaVPNMayo import RegistroSchemaVPNMayo
from schemas.schemaRFC import RegistroSchemaRFC
from routes.route import FileGeneratorRoute  
from schemas.schemaTel import RegistroSchemaTel
from schemas.schemaInter import RegistroSchemaInter
from schemas.schemaActualizarMemo import ActualizacionMemorando
from schemas.schemaActualizarFuncionRol import ActualizacionFuncionRol
from services.service import Service
from models.model import BDModel

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

logger = Logger()

# Schema
form_schemaVPN = RegistroSchemaVPN()
form_schemaVPNMayo = RegistroSchemaVPNMayo()
form_schemaTel = RegistroSchemaTel()
form_schemaRFC = RegistroSchemaRFC() 
forms_schemaInter = RegistroSchemaInter()

actualizarMemo = ActualizacionMemorando()
actualizarFuncionRol = ActualizacionFuncionRol()

# Model
db_conn = BDModel()
db_conn.connect_to_database()

# Service
service = Service(db_conn)

# Routes
form_routes = FileGeneratorRoute(service, form_schemaVPN, form_schemaVPNMayo, form_schemaTel, form_schemaRFC, forms_schemaInter, actualizarMemo, actualizarFuncionRol)

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