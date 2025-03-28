from flask import Flask, request, jsonify, send_file
from logger.logger import Logger
from schemas.schema import RegistroSchema 
from schemas.schemaRFC import RegistroSchema2
from routes.route import FileGeneratorRoute  

app = Flask(__name__)

#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

logger = Logger()

# Schema
form_schema = RegistroSchema()

form_schemaRFC = RegistroSchema2()  

# Routes
form_routes = FileGeneratorRoute(form_schema, form_schemaRFC)

#Blueprint
app.register_blueprint(form_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)