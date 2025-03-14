from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from csv import writer
from fpdf import FPDF
import pandas as pd
from logger.logger import Logger
import os
from marshmallow import ValidationError

class FileGeneratorRoute(Blueprint):
    """Class to handle the routes for file generation"""

    def __init__(self,forms_schema):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.forms_schema = forms_schema
        self.register_routes()

    def register_routes(self):
        """Function to register the routes for file generation"""
        self.route("/api/v1/generar-pdf", methods=["POST"])(self.generar_pdf)
        self.route("/healthcheck", methods=["GET"])(self.healthcheck)

    def fetch_request_data(self):
        """Function to fetch the request data"""
        try:
            request_data = request.json
            if not request_data:
                return 400, "Invalid data", None
            return 200, None, request_data
        except Exception as e:
            self.logger.error(f"Error fetching request data: {e}")
            return 500, "Error fetching request data", None

    
    def generar_pdf(self):
        try:
            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            validated_data = self.forms_schema.load(data)

            with open('/app/data/datos.txt','w') as file: 
                file.write("\\newcommand{\\NOMBRE}{"+ validated_data.get('nombre')+"}"+ os.linesep)
                file.write("\\newcommand{\\PUESTO}{"+ validated_data.get('puesto') + "}"+ os.linesep)
                file.write("\\newcommand{\\UA}{" + validated_data.get('ua') + "}"+ os.linesep)
                file.write("\\newcommand{\\ID}{" + validated_data.get('id') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXT}{" + validated_data.get('extension') + "}"+ os.linesep)
                file.write("\\newcommand{\\CORREO}{" + validated_data.get('correo')+ "}"+ os.linesep)
                file.write("\\newcommand{\\MARCA}{" + validated_data.get('marca') + "}"+ os.linesep)
                file.write ("\\newcommand{\\MODELO}{" + validated_data.get('modelo') + "}"+ os.linesep)
                file.write("\\newcommand{\\SERIE}{"+ validated_data.get('serie') + "}"+ os.linesep)
                file.write("\\newcommand{\\MACADDRESS}{"+ validated_data.get('macadress') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREJEFE}{"+ validated_data.get('jefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOJEFE}{"+ validated_data.get('puestojefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\SERVICIOS}{" + validated_data.get('servicios') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICACION}{" + validated_data.get('justificacion') + "}"+ os.linesep)
                file.write("\\newcommand{\\PRUEBA}{" + validated_data.get('malware') + "}"+ os.linesep)

            df = pd.DataFrame([validated_data])
            df.to_csv('/app/data/out.csv', index=False, mode='a')

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            text = f"Nombre: {validated_data.get('nombre')}\nCorreo: {validated_data.get('correo')}\nPuesto: {validated_data.get('puesto')}\nID: {validated_data.get('id')}\nExtensión: {validated_data.get('extension')}"
            pdf.multi_cell(0, 10, text)

            output = BytesIO()
            pdf.output(output)
            output.seek(0)
            return send_file(
                output,
                mimetype="application/pdf",
                download_name="registro.pdf",
                as_attachment=True,
            )
        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500


    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200