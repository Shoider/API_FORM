import subprocess
import pandas as pd
import tempfile
import shutil
import os

from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from logger.logger import Logger
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

            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            validated_data = self.forms_schema.load(data)

            # Transformar valores "SI" y "NO"
            sianti = "x" if validated_data.get('malware') == "SI" else " "
            noanti = "x" if validated_data.get('malware') == "NO" else " "

            sivige = "x" if validated_data.get('vigencia') == "SI" else " "
            novige = "x" if validated_data.get('vigencia') == "NO" else " "

            siso = "x" if validated_data.get('so') == "SI" else " "
            noso = "x" if validated_data.get('so') == "NO" else " "

            silic = "x" if validated_data.get('licencia') == "SI" else " "
            nolic = "x" if validated_data.get('licencia') == "NO" else " "

            alta = "x" if validated_data.get('movimiento') == "ALTA" else " "
            baja = "x" if validated_data.get('movimiento') == "BAJA" else " "
            cambio = "x" if validated_data.get('movimiento') == "CAMBIO" else " "

            # Crear Datos.txt en el directorio temporal
            datos_txt_path = os.path.join(temp_dir, "Datos.txt")
            with open(datos_txt_path, 'w') as file: 
                file.write("\\newcommand{\\NOMBRE}{"+ validated_data.get('nombre')+"}"+ os.linesep)
                file.write("\\newcommand{\\PUESTO}{"+ validated_data.get('puesto') + "}"+ os.linesep)
                file.write("\\newcommand{\\UA}{" + validated_data.get('ua') + "}"+ os.linesep)
                file.write("\\newcommand{\\ID}{" + validated_data.get('id') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXT}{" + validated_data.get('extension') + "}"+ os.linesep)
                file.write("\\newcommand{\\CORREO}{" + validated_data.get('correo')+ "}"+ os.linesep)
                file.write("\\newcommand{\\MARCA}{" + validated_data.get('marca') + "}"+ os.linesep)
                file.write("\\newcommand{\\MODELO}{" + validated_data.get('modelo') + "}"+ os.linesep)
                file.write("\\newcommand{\\SERIE}{"+ validated_data.get('serie') + "}"+ os.linesep)
                file.write("\\newcommand{\\MACADDRESS}{"+ validated_data.get('macadress') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREJEFE}{"+ validated_data.get('jefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOJEFE}{"+ validated_data.get('puestojefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\SERVICIOS}{" + validated_data.get('servicios') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICACION}{" + validated_data.get('justificacion') + "}"+ os.linesep)

                file.write("\\newcommand{\\SIANTI}{" + sianti + "}" + os.linesep)
                file.write("\\newcommand{\\NOANTI}{" + noanti + "}" + os.linesep)
                file.write("\\newcommand{\\SIVIGE}{" + sivige + "}" + os.linesep)
                file.write("\\newcommand{\\NOVIGE}{" + novige + "}" + os.linesep)
                file.write("\\newcommand{\\SISO}{" + siso + "}" + os.linesep)
                file.write("\\newcommand{\\NOSO}{" + noso + "}" + os.linesep)
                file.write("\\newcommand{\\SILIC}{" + silic + "}" + os.linesep)
                file.write("\\newcommand{\\NOLIC}{" + nolic + "}" + os.linesep)
                file.write("\\newcommand{\\ALTA}{" + alta + "}" + os.linesep)
                file.write("\\newcommand{\\BAJA}{" + baja + "}" + os.linesep)
                file.write("\\newcommand{\\CAMBIO}{" + cambio + "}" + os.linesep)

            # Crear out.csv en el directorio temporal
            out_csv_path = os.path.join(temp_dir, "out.csv")
            df = pd.DataFrame([validated_data])
            df.to_csv(out_csv_path, index=False, mode='a')

            # Compilar / Generar pdf en el directorio temporal
            archivo_tex = os.path.join(temp_dir, "Formato_VPN_241105.tex")
            nombre_pdf = os.path.join(temp_dir, "Formato_VPN_241105.pdf")

            # Copia Formato_VPN_241105.tex del directorio /app/data al directorio temporal
            shutil.copy("/app/data/Formato_VPN_241105.tex", archivo_tex)

            # Copiar imágenes al directorio temporal
            imagenes_dir = os.path.join(temp_dir, "imagenes")
            shutil.copytree("/app/imagenes", imagenes_dir)

            try:
                subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
            except:
                self.logger.error(f"Error generando PDF: {e}")
                return jsonify({"error": f"Error al compilar LaTeX: {e}"}), 500
            
            # Cargar pdf
            output = BytesIO()
            with open(nombre_pdf, "rb") as pdf_file:
                output.write(pdf_file.read())
            output.seek(0)

            # Enviar archivo
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
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)


    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200