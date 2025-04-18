from flask import Flask, request, jsonify, send_file
from logger.logger import Logger
from schemas.schemaVPN import RegistroSchemaVPN
from schemas.schemaRFC import RegistroSchemaRFC
from routes.route import FileGeneratorRoute  
from schemas.schemaTel import RegistroSchemaTel
from schemas.schemaInter import RegistroSchemaInter

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

logger = Logger()

# Schema
form_schemaVPN = RegistroSchemaVPN()
form_schemaTel = RegistroSchemaTel()
form_schemaRFC = RegistroSchemaRFC() 
forms_schemaInter = RegistroSchemaInter()

# Routes
form_routes = FileGeneratorRoute(form_schemaVPN, form_schemaTel, form_schemaRFC, forms_schemaInter)

#Blueprint
app.register_blueprint(form_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)