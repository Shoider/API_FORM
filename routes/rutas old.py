from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from csv import writer
from fpdf import FPDF
from logger.logger import Logger

class FileGeneratorRoute(Blueprint):
    """Class to handle the routes for file generation"""

    def __init__(self):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.register_routes()

    def register_routes(self):
        """Function to register the routes for file generation"""
        self.route("/api/v1/generar-csv", methods=["POST"])(self.generar_csv)
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

    def generar_csv(self):
        """Generate a CSV file from form data"""
        code, message, data = self.fetch_request_data()
        if code != 200:
            return jsonify({"error": message}), code
        try:
            output = BytesIO()
            csv_writer = writer(output)
            header = ["Nombre", "Correo", "Puesto", "ID", "Extensión"]
            csv_writer.writerow(header)
            row = [data.get("nombre"), data.get("correo"), data.get("puesto"), data.get("id"), data.get("extension")]
            csv_writer.writerow(row)
            output.seek(0)
            return send_file(
                output,
                mimetype="text/csv",
                download_name="registro.csv",
                as_attachment=True,
            )
        except Exception as e:
            self.logger.error(f"Error generating CSV: {e}")
            return jsonify({"error": "Error generating CSV"}), 500
    
    def generar_pdf(self):
        """Generate a PDF file from form data"""
        code, message, data = self.fetch_request_data()
        if code != 200:
            return jsonify({"error": message}), code
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            text = f"Nombre: {data.get('nombre')}\nCorreo: {data.get('correo')}\nPuesto: {data.get('puesto')}\nID: {data.get('id')}\nExtensión: {data.get('extension')}"
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
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            return jsonify({"error": "Error generating PDF"}), 500


    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200