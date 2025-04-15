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

    def __init__(self,forms_schemaVPN, forms_schemaTel, forms_schemaRFC, forms_schemaInter):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.forms_schemaVPN = forms_schemaVPN
        self.forms_schemaTel = forms_schemaTel
        self.forms_schemaRFC = forms_schemaRFC
        self.forms_schemaInter = forms_schemaInter
        self.register_routes()

    def register_routes(self):
        """Function to register the routes for file generation"""
        self.route("/api/v1/vpn", methods=["POST"])(self.vpn)
        self.route("/api/v1/tel", methods=["POST"])(self.tel)
        self.route("/api/v1/rfc", methods=["POST"])(self.rfc)
        self.route("/api/v1/inter", methods=["POST"])(self.inter)
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
        
    def crear_csv_desde_registros(self, temp_dir, nombre_archivo_csv, registros):
        """
        Crea un archivo CSV a partir de un array de registros,
        con la columna 'id' siempre renombrada a 'No'.

        Args:
            temp_dir (str): Directorio temporal donde se guardará el CSV.
            nombre_archivo_csv (str): Nombre del archivo CSV a crear.
            registros (list): Array de diccionarios con los registros.
        """
        try:
            out_csv_path = os.path.join(temp_dir, nombre_archivo_csv)

            if not registros:
                df = pd.DataFrame([{}], columns=['id', 'SO', 'FRO', 'IPO', 'SD', 'FRD', 'IPD', 'PRO', 'PUER'])

            for registro in registros:
                registro.pop('isNew', None)
                if "IPO" in registro:
                    registro["IPO"] = registro["IPO"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                if "IPD" in registro:
                    registro["IPD"] = registro["IPD"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                if "SO" in registro:
                    registro["SO"] = registro["SO"].replace(" ", "\\\\").replace(", ", "\\\\")
                if "SD" in registro:
                    registro["SD"] = registro["SD"].replace(" ", "\\\\").replace(", ", "\\\\")
                if "FRO" in registro:
                    registro["FRO"] = registro["FRO"].replace(" ", "\\\\").replace(", ", "\\\\")
                if "FRD" in registro:
                    registro["FRD"] = registro["FRD"].replace(" ", "\\\\").replace(", ", "\\\\")

            df = pd.DataFrame(registros)
            df = df.rename(columns={'id': 'N'})  # Siempre renombra 'id' a 'N'
            df.to_csv(out_csv_path, index=False, mode='x')

            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}")

    def modificar_registros_id(self, registros):
        """
        Modifica el array de registros para concatenar "*C" y un salto de línea a la columna "id".

        Args:
            registros (list): El array de registros a modificar.
        """
        if not registros:
            print("El array de registros está vacío.")
            return

        for registro in registros:
            if "id" in registro:
                #registro["id"] = str(registro["id"]) + "\\\\C*"  # Concatena "*C" y un salto de línea
                registro["id"]= "*C" + str(registro["id"])

    
    def vpn(self):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            # Validacion
            validated_data = self.forms_schemaVPN.load(data)
            
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

                file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)##PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----

            # Crear out.csv en el directorio temporal
            # out_csv_path = os.path.join(temp_dir, "out.csv")
            # df = pd.DataFrame([validated_data])
            # df.to_csv(out_csv_path, index=False, mode='a')

            # Preparar archivos en el directorio temporal
            archivo_tex = os.path.join(temp_dir, "Formato_VPN_241105.tex")
            nombre_pdf = os.path.join(temp_dir, "Formato_VPN_241105.pdf")

            # Copia Formato_VPN_241105.tex del directorio /app/data al directorio temporal
            shutil.copy("/app/latex/Formato_VPN_241105.tex", archivo_tex)

            # Copiar imágenes al directorio temporal
            imagenes_dir = os.path.join(temp_dir, "imagenes")
            shutil.copytree("/app/latex/imagenes", imagenes_dir)

            # Compilar latex Aux
            try:
                subprocess.run(['latex',  "-output-directory",  temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo .aux generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando archivo .aux: {e}")
                return jsonify({"error": f"Error al compilar LaTeX Aux: {e}"}), 500

            # Compilar latex PDF
            try:
                subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo PDF generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando PDF: {e}")
                return jsonify({"error": f"Error al compilar LaTeX PDF: {e}"}), 500
            
            # Cargar pdf
            output = BytesIO()
            with open(nombre_pdf, "rb") as pdf_file:
                output.write(pdf_file.read())
            output.seek(0)

            # Enviar archivo
            return send_file(
                output,
                mimetype="application/pdf",
                download_name="Registro_VPN.pdf",
                as_attachment=True,
            )
        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "Detalles": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)

    def tel(self):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            # Validacion
            validated_data = self.forms_schemaTel.load(data)
            
            # Tipo de Movimiento
            alta = "X" if validated_data.get('movimiento') == "ALTA" else " "
            baja = "X" if validated_data.get('movimiento') == "BAJA" else " "
            cambio = "X" if validated_data.get('movimiento') == "CAMBIO" else " "

            # Direccion
            direcion = validated_data.get('direccion') + ", " + validated_data.get('piso') + ", " + validated_data.get('ala')

            # Traducir valores true y false #PENDIGN
            externo = "true" if validated_data.get('usuaExterno') == True else "false"

            # Transformar valores "X" y " "
            siMundo = "X" if validated_data.get('mundo') == "SI" else " "
            noMundo = "X" if validated_data.get('mundo') == "NO" else " "
            siLocal = "X" if validated_data.get('local') == "SI" else " "
            noLocal = "X" if validated_data.get('local') == "NO" else " "
            sicLocal = "X" if validated_data.get('cLocal') == "SI" else " "
            nocLocal = "X" if validated_data.get('cLocal') == "NO" else " "
            siNacional = "X" if validated_data.get('nacional') == "SI" else " "
            noNacional = "X" if validated_data.get('nacional') == "NO" else " "
            sicNacional = "X" if validated_data.get('cNacional') == "SI" else " "
            nocNacional = "X" if validated_data.get('cNacional') == "NO" else " "
            siEua = "X" if validated_data.get('eua') == "SI" else " "
            noEua = "X" if validated_data.get('eua') == "NO" else " "

            # Crear Datos.txt en el directorio temporal
            datos_txt_path = os.path.join(temp_dir, "Datos.txt")
            
            with open(datos_txt_path, 'w') as file: 
                file.write("\\newcommand{\\ALTA}{" + alta + "}" + os.linesep)
                file.write("\\newcommand{\\BAJA}{" + baja + "}" + os.linesep)
                file.write("\\newcommand{\\CAMBIO}{" + cambio + "}" + os.linesep)

                file.write("\\newcommand{\\TIPOUSUARIO}{"+ validated_data.get('tipoUsuario')+"}"+ os.linesep)

                file.write("\\newcommand{\\ACTIVACION}{"+ validated_data.get('activacion') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXPIRACION}{" + validated_data.get('expiracion') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREUSUARIO}{" + validated_data.get('nombreUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\CORREOUSUARIO}{" + validated_data.get('correoUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\DIRECCION}{" + direcion + "}"+ os.linesep)
                file.write("\\newcommand{\\UAUSUARIO}{" + validated_data.get('uaUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREEMPLEADO}{" + validated_data.get('nombreEmpleado')+ "}"+ os.linesep)
                file.write("\\newcommand{\\IDEMPLEADO}{" + validated_data.get('idEmpleado') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXTEMPLEADO}{" + validated_data.get('extEmpleado') + "}"+ os.linesep)
                file.write("\\newcommand{\\CORREOEMPLEADO}{"+ validated_data.get('correoEmpleado') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOEMPLEADO}{"+ validated_data.get('puestoEmpleado') + "}"+ os.linesep)

                file.write("\\newcommand{\\SIMUNDO}{" + siMundo + "}" + os.linesep)
                file.write("\\newcommand{\\NOMUNDO}{" + noMundo + "}" + os.linesep)
                file.write("\\newcommand{\\SILOCAL}{" + siLocal + "}" + os.linesep)
                file.write("\\newcommand{\\NOLOCAL}{" + noLocal + "}" + os.linesep)
                file.write("\\newcommand{\\SICLOCAL}{" + sicLocal + "}" + os.linesep)
                file.write("\\newcommand{\\NOCLOCAL}{" + nocLocal + "}" + os.linesep)
                file.write("\\newcommand{\\SINACIONAL}{" + siNacional + "}" + os.linesep)
                file.write("\\newcommand{\\NONACIONAL}{" + noNacional + "}" + os.linesep)
                file.write("\\newcommand{\\SICNACIONAL}{" + sicNacional + "}" + os.linesep)
                file.write("\\newcommand{\\NOCNACIONAL}{" + nocNacional + "}" + os.linesep)
                file.write("\\newcommand{\\SIEUA}{" + siEua + "}" + os.linesep)
                file.write("\\newcommand{\\NOEUA}{" + noEua + "}" + os.linesep)

                file.write("\\newcommand{\\JUSTIFICACION}{"+ validated_data.get('justificacion') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOUSUARIO}{"+ validated_data.get('puestoUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREJEFE}{" + validated_data.get('nombreJefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOJEFE}{" + validated_data.get('puestoJefe') + "}"+ os.linesep) 

                file.write("\\newcommand{\\EXTERNO}{" + externo + "}" + os.linesep)
                file.write("\\newcommand{\\MARCA}{" + validated_data.get('marca') + "}" + os.linesep)
                file.write("\\newcommand{\\MODELO}{" + validated_data.get('modelo') + "}" + os.linesep)
                file.write("\\newcommand{\\SERIE}{" + validated_data.get('serie') + "}" + os.linesep)
                file.write("\\newcommand{\\VERSION}{" + validated_data.get('version') + "}" + os.linesep)

                file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)##PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----

            # Preparar archivos en el directorio temporal
            archivo_tex = os.path.join(temp_dir, "Formato_TELEFONIA.tex")
            nombre_pdf = os.path.join(temp_dir, "Formato_TELEFONIA.pdf")

            # Copia Formato_TELEFONIA.tex del directorio /app/data al directorio temporal
            shutil.copy("/app/latex/Formato_TELEFONIA.tex", archivo_tex)

            # Copiar imágenes al directorio temporal
            imagenes_dir = os.path.join(temp_dir, "imagenes")
            shutil.copytree("/app/latex/imagenes", imagenes_dir)

            # Compilar latex Aux
            try:
                subprocess.run(['latex',  "-output-directory",  temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo .aux generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando archivo .aux: {e}")
                return jsonify({"error": f"Error al compilar LaTeX Aux: {e}"}), 500

            # Compilar latex PDF
            try:
                subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo PDF generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando PDF: {e}")
                return jsonify({"error": f"Error al compilar LaTeX PDF: {e}"}), 500
            
            # Cargar pdf
            output = BytesIO()
            with open(nombre_pdf, "rb") as pdf_file:
                output.write(pdf_file.read())
            output.seek(0)

            # Enviar archivo
            return send_file(
                output,
                mimetype="application/pdf",
                download_name="RegistroTelefonia.pdf",
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

    def rfc(self):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            # Validacion
            validated_data = self.forms_schemaRFC.load(data)           

            # Transformar valores "X" y " " para Tipo de Movimiento
            intersistemas = "x" if validated_data.get('intersistemas') == True else " "
            administrador = "x" if validated_data.get('administrador') == True else " "
            desarrollador = "x" if validated_data.get('desarrollador') == True else " "
            usuario = "x" if validated_data.get('usuario') == True else " "
            otro = "x" if validated_data.get('otro') == True else " "

            # Booleanos para Tipo de Movimiento
            intersistemasBool = "true" if validated_data.get('intersistemas') == True else "false"
            administradorBool = "true" if validated_data.get('administrador') == True else "false"
            desarrolladorBool = "true" if validated_data.get('desarrollador') == True else "false"
            usuarioBool = "true" if validated_data.get('usuario') == True else "false"
            otroBool = "true" if validated_data.get('otro') == True else "false"

            # Booleanos para Generacion de tablas
            AltaInter = "true" if validated_data.get('AltaInter') == True else "false"
            BajaInter = "true" if validated_data.get('BajaInter') == True else "false"
            AltaAdmin = "true" if validated_data.get('AltaAdmin') == True else "false"
            BajaAdmin = "true" if validated_data.get('BajaAdmin') == True else "false"
            AltaDes = "true" if validated_data.get('AltaDes') == True else "false"
            BajaDes = "true" if validated_data.get('BajaDes') == True else "false"
            AltaUsua = "true" if validated_data.get('AltaUsua') == True else "false"
            BajaUsua = "true" if validated_data.get('BajaUsua') == True else "false"
            AltaOtro = "true" if validated_data.get('AltaOtro') == True else "false"
            BajaOtro = "true" if validated_data.get('BajaOtro') == True else "false"

            # En caso de cambios
            if validated_data.get('CambioInter') == True:
                AltaInter = "true"
                BajaInter = "true"
            if validated_data.get('CambioAdmin') == True:
                AltaAdmin = "true"
                BajaAdmin = "true"
            if validated_data.get('CambioDes') == True:
                AltaDes = "true"
                BajaDes = "true"
            if validated_data.get('CambioUsua') == True:
                AltaUsua = "true"
                BajaUsua = "true"
            if validated_data.get('CambioOtro') == True:
                AltaOtro = "true"
                BajaOtro = "true"

            # Desotro valor default
            desotro_value = validated_data.get('desotro', '')

            # Unir Justificaciones
            justifica1 = validated_data.get('justifica')
            justifica2 = validated_data.get('justifica2')
            justifica3 = validated_data.get('justifica3')

            justifica_combined = justifica1 + ". " + justifica2 + ". " + justifica3  # Concatenar con espacios

            # Crear Datos.txt en el directorio temporal
            datos_txt_path = os.path.join(temp_dir, "Datos.txt")
            with open(datos_txt_path, 'w') as file: 
                file.write("\\newcommand{\\TEMPO}{"+ validated_data.get('tempo')+"}"+ os.linesep)
                file.write("\\newcommand{\\MEMO}{"+ validated_data.get('memo') + "}"+ os.linesep)
                file.write("\\newcommand{\\DESCBREVE}{" + validated_data.get('descbreve') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMEI}{"+ validated_data.get('nomei') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXTEI}{"+ validated_data.get('extei') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMS}{"+ validated_data.get('noms') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXTS}{" + validated_data.get('exts') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOS}{" + validated_data.get('puestos') + "}"+ os.linesep)
                file.write("\\newcommand{\\AREAS}{" + validated_data.get('areas') + "}"+ os.linesep)
                file.write("\\newcommand{\\DESDET}{" + validated_data.get('desdet') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICA}{" + justifica_combined + "}" + os.linesep)
                file.write("\\newcommand{\\NOMBREJEFE}{" + validated_data.get('nombreJefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOJEFE}{" + validated_data.get('puestoJefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOEI}{" + validated_data.get('puestoei') + "}"+ os.linesep)

                # Tablas
                file.write("\\newcommand{\\INTER}{" + intersistemas + "}" + os.linesep)
                file.write("\\newcommand{\\ADMIN}{" + administrador + "}" + os.linesep)
                file.write("\\newcommand{\\DES}{" + desarrollador + "}" + os.linesep)
                file.write("\\newcommand{\\USUA}{" + usuario + "}" + os.linesep)
                file.write("\\newcommand{\\OTRO}{" + otro + "}" + os.linesep)

                file.write("\\newcommand{\\INTERBOOL}{" + intersistemasBool + "}" + os.linesep)
                file.write("\\newcommand{\\ADMINBOOL}{" + administradorBool + "}" + os.linesep)
                file.write("\\newcommand{\\DESBOOL}{" + desarrolladorBool + "}" + os.linesep)
                file.write("\\newcommand{\\USUABOOL}{" + usuarioBool + "}" + os.linesep)
                file.write("\\newcommand{\\OTROBOOL}{" + otroBool + "}" + os.linesep)

                file.write("\\newcommand{\\DESOTRO}{"+ desotro_value + "}"+ os.linesep)

                file.write("\\newcommand{\\ALTASINTER}{" + AltaInter + "}" + os.linesep)
                file.write("\\newcommand{\\BAJASINTER}{" + BajaInter + "}" + os.linesep)
                file.write("\\newcommand{\\ALTASADMIN}{" + AltaAdmin + "}" + os.linesep)
                file.write("\\newcommand{\\BAJASADMIN}{" + BajaAdmin + "}" + os.linesep)
                file.write("\\newcommand{\\ALTASDES}{" + AltaDes + "}" + os.linesep)
                file.write("\\newcommand{\\BAJASDES}{" + BajaDes + "}" + os.linesep)
                file.write("\\newcommand{\\ALTASUSUA}{" + AltaUsua + "}" + os.linesep)
                file.write("\\newcommand{\\BAJASUSUA}{" + BajaUsua + "}" + os.linesep)
                file.write("\\newcommand{\\ALTASOTRO}{" + AltaOtro + "}" + os.linesep)
                file.write("\\newcommand{\\BAJASOTRO}{" + BajaOtro + "}" + os.linesep)
                
                file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)##PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----

            ###### Aqui funciona Generalmente, Abajo esta dificil de entender

            # Tablas csv

            # Intersistemas
            # Cambios
            registrosAltas = validated_data.get('registrosInterCambiosAltas', [])  # Obtiene array de los datos
            registrosBajas = validated_data.get('registrosInterCambiosBajas', [])  # Obtiene array de los datos
            # Añadir que viene de Cambios "C*"
            self.modificar_registros_id(registrosAltas)
            self.modificar_registros_id(registrosBajas)
            
            # Altas
            registros = validated_data.get('registrosInterAltas', [])   # Obtiene array de los datos
            registros.extend(registrosAltas)                            # Unir registros de altas y cambios
            self.crear_csv_desde_registros(temp_dir, "ALTASINTER.csv", registros) #Se cambia el nombre de la columna
            # Bajas
            registros = validated_data.get('registrosInterBajas', [])   # Obtiene array de los datos
            registros.extend(registrosBajas)                            # Unir registros de bajas y cambios
            self.crear_csv_desde_registros(temp_dir, "BAJASINTER.csv", registros) #Se cambia el nombre de la columna

            # Administrador
            # Cambios
            registrosAltas = validated_data.get('registrosAdminCambiosAltas', [])
            registrosBajas = validated_data.get('registrosAdminCambiosBajas', [])
            # Añadir que viene de Cambios "C*"
            self.modificar_registros_id(registrosAltas)
            self.modificar_registros_id(registrosBajas)
            # Altas
            registros = validated_data.get('registrosAdminAltas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "ALTASADMIN.csv", registros) #Se cambia el nombre de la columna
            # Bajas
            registros = validated_data.get('registrosAdminBajas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "BAJASADMIN.csv", registros) #Se cambia el nombre de la columna

            # Desarrollador
            # Cambios
            registrosAltas = validated_data.get('registrosDesCambiosAltas', [])
            registrosBajas = validated_data.get('registrosDesCambiosBajas', [])
            # Añadir que viene de Cambios "C*"
            self.modificar_registros_id(registrosAltas)
            self.modificar_registros_id(registrosBajas)
            # Altas
            registros = validated_data.get('registrosDesAltas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "ALTASDES.csv", registros) #Se cambia el nombre de la columna
            # Bajas
            registros = validated_data.get('registrosDesBajas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "BAJASDES.csv", registros) #Se cambia el nombre de la columna

            # Usuario
            # Cambios
            registrosAltas = validated_data.get('registrosUsuaCambiosAltas', [])
            registrosBajas = validated_data.get('registrosUsuaCambiosBajas', [])
            # Añadir que viene de Cambios "C*"
            self.modificar_registros_id(registrosAltas)
            self.modificar_registros_id(registrosBajas)
            # Altas
            registros = validated_data.get('registrosUsuaAltas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "ALTASUSUA.csv", registros) #Se cambia el nombre de la columna
            # Bajas
            registros = validated_data.get('registrosUsuaBajas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "BAJASUSUA.csv", registros) #Se cambia el nombre de la columna

            # Otro
            # Cambios
            registrosAltas = validated_data.get('registrosOtroCambiosAltas', [])
            registrosBajas = validated_data.get('registrosOtroCambiosBajas', [])
            # Añadir que viene de Cambios "C*"
            self.modificar_registros_id(registrosAltas)
            self.modificar_registros_id(registrosBajas)
            # Altas
            registros = validated_data.get('registrosOtroAltas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "ALTASOTRO.csv", registros) #Se cambia el nombre de la columna
            # Bajas
            registros = validated_data.get('registrosOtroBajas', [])  # Obtiene array de los datos
            self.crear_csv_desde_registros(temp_dir, "BAJASOTRO.csv", registros) #Se cambia el nombre de la columna

            # Preparar archivos en el directorio temporal
            archivo_tex = os.path.join(temp_dir, "Formato_RFC_LT.tex")
            nombre_pdf = os.path.join(temp_dir, "Formato_RFC_LT.pdf")

            # Copia Formato_RFC_LT.tex del directorio /app/data al directorio temporal
            shutil.copy("/app/latex/Formato_RFC_LT.tex", archivo_tex)

            # Copiar imágenes al directorio temporal
            imagenes_dir = os.path.join(temp_dir, "imagenes")
            shutil.copytree("/app/latex/imagenes", imagenes_dir)

            # Compilar latex Aux
            try:
                subprocess.run(['latex',  "-output-directory",  temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo .aux generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando archivo .aux: {e}")
                return jsonify({"error": f"Error al compilar LaTeX Aux: {e}"}), 500

            # Compilar latex PDF
            try:
                subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo PDF generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando PDF: {e}")
                return jsonify({"error": f"Error al compilar LaTeX PDF: {e}"}), 500

            # Cargar pdf
            output = BytesIO()
            with open(nombre_pdf, "rb") as pdf_file:
                output.write(pdf_file.read())
            output.seek(0)

            # Enviar archivo
            return send_file(
                output,
                mimetype="application/pdf",
                download_name="RegistroRFC.pdf",
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
            #shutil.rmtree(temp_dir)
            self.logger.info(f"Directorio temporal {temp_dir} no eliminado.")

    def inter(self):
        try: 
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            # Validacion
            validated_data = self.forms_schemaInter.load(data)
            
            # Transformar valores "SI" y "NO"
            descarga = "x" if validated_data.get('descarga') == True else " "
            foros = "x" if validated_data.get('foros') == True else " "
            comercio = "x" if validated_data.get('comercio') == True else " "
            redes = "x" if validated_data.get('redes') == True else " "
            videos = "x" if validated_data.get('videos') == True else " "
            whats = "x" if validated_data.get('whats') == True else " "
            dropbox = "x" if validated_data.get('dropbox') == True else " "
            onedrive = "x" if validated_data.get('onedrive') == True else " "
            skype = "x" if validated_data.get('skype') == True else " "
            wetransfer = "x" if validated_data.get('wetransfer') == True else " "
            team = "x" if validated_data.get('team') == True else " "
            otra = "x" if validated_data.get('otra') == True else " "
            otra2 = "x" if validated_data.get('otra2') == True else " "
            otra3 = "x" if validated_data.get('otra3') == True else " "
            otra4 = "x" if validated_data.get('otra4') == True else " "

            descargabool = "true" if validated_data.get('descarga') == True else "false"
            forosbool = "true" if validated_data.get('foros') == True else "false"
            comerciobool = "true" if validated_data.get('comercio') == True else "false"
            redesbool = "true" if validated_data.get('redes') == True else "false"
            videosbool = "true" if validated_data.get('videos') == True else "false"
            whatsbool = "true" if validated_data.get('whats') == True else "false"
            dropboxbool = "true" if validated_data.get('dropbox') == True else "false"
            onedrivebool = "true" if validated_data.get('onedrive') == True else "false"
            skypebool = "true" if validated_data.get('skype') == True else "false"
            wetransferbool = "true" if validated_data.get('wetransfer') == True else "false"
            teambool = "true" if validated_data.get('team') == True else "false"
            otrabool = "true" if validated_data.get('otra') == True else "false"
            otrabool2 = "true" if validated_data.get('otra2') == True else "false"
            otrabool3 = "true" if validated_data.get('otra3') == True else "false"
            otrabool4 = "true" if validated_data.get('otra4') == True else "false"

            direcConAla = validated_data.get("direccion") + ", "+ validated_data.get("piso") + ", " + validated_data.get("ala")

            # Crear Datos.txt en el directorio temporal
            datos_txt_path = os.path.join(temp_dir, "Datos.txt")
            with open(datos_txt_path, 'w') as file: 
                file.write("\\newcommand{\\FECHASOLI}{"+ validated_data.get('fechasoli')+"}"+ os.linesep)
                file.write("\\newcommand{\\UAUSUARIO}{"+ validated_data.get('uaUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\AREAUSUARIO}{"+ validated_data.get('areaUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREUSUARIO}{" + validated_data.get('nombreUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOUSUARIO}{" + validated_data.get('puestoUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\IPUSUARIO}{" + validated_data.get('ipUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\CORREOUSUARIO}{" + validated_data.get('correoUsuario')+ "}"+ os.linesep)
                file.write("\\newcommand{\\TELUSUARIO}{" + validated_data.get('teleUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\EXTUSUARIO}{" + validated_data.get('extUsuario') + "}"+ os.linesep)
                file.write("\\newcommand{\\NOMBREJEFE}{"+ validated_data.get('nombreJefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\PUESTOJEFE}{"+ validated_data.get('puestoJefe') + "}"+ os.linesep)
                file.write("\\newcommand{\\DIRECCION}{"+ direcConAla +  "}"+ os.linesep)

                file.write("\\newcommand{\\DESCARGA}{" + descarga + "}" + os.linesep)
                file.write("\\newcommand{\\FOROS}{" + foros + "}" + os.linesep)
                file.write("\\newcommand{\\COMERCIO}{" + comercio + "}" + os.linesep)
                file.write("\\newcommand{\\REDES}{" + redes + "}" + os.linesep)
                file.write("\\newcommand{\\VIDEOS}{" + videos + "}" + os.linesep)
                file.write("\\newcommand{\\WHATS}{" + whats + "}" + os.linesep)
                file.write("\\newcommand{\\DROPBOX}{" + dropbox + "}" + os.linesep)
                file.write("\\newcommand{\\ONEDRIVE}{" + onedrive + "}" + os.linesep)
                file.write("\\newcommand{\\SKYPE}{" + skype + "}" + os.linesep)
                file.write("\\newcommand{\\WETRANSFER}{" + wetransfer + "}" + os.linesep)
                file.write("\\newcommand{\\TEAM}{" + team + "}" + os.linesep)
                file.write("\\newcommand{\\OTRA}{" + otra + "}" + os.linesep)

                file.write("\\newcommand{\\OTRAdos}{" + otra2 + "}" + os.linesep)
                file.write("\\newcommand{\\OTRAtres}{" + otra3 + "}" + os.linesep)
                file.write("\\newcommand{\\OTRAcuatro}{" + otra4 + "}" + os.linesep)

                file.write("\\newcommand{\\OTRAC}{"+ validated_data.get('otraC') + "}"+ os.linesep)

                file.write("\\newcommand{\\OTRACdos}{"+ validated_data.get('otraC2') + "}"+ os.linesep)
                file.write("\\newcommand{\\OTRACtres}{"+ validated_data.get('otraC3') + "}"+ os.linesep)
                file.write("\\newcommand{\\OTRACcuatro}{"+ validated_data.get('otraC4') + "}"+ os.linesep)
                
                file.write("\\newcommand{\\DESCARGABOOL}{" + descargabool + "}" + os.linesep)
                file.write("\\newcommand{\\FOROSBOOL}{" + forosbool + "}" + os.linesep)
                file.write("\\newcommand{\\COMERCIOBOOL}{" + comerciobool + "}" + os.linesep)
                file.write("\\newcommand{\\REDESBOOL}{" + redesbool + "}" + os.linesep)
                file.write("\\newcommand{\\VIDEOSBOOL}{" + videosbool + "}" + os.linesep)
                file.write("\\newcommand{\\WHATSBOOL}{" + whatsbool + "}" + os.linesep)
                file.write("\\newcommand{\\DROPBOXBOOL}{" + dropboxbool + "}" + os.linesep)
                file.write("\\newcommand{\\ONEDRIVEBOOL}{" + onedrivebool + "}" + os.linesep)
                file.write("\\newcommand{\\SKYPEBOOL}{" + skypebool + "}" + os.linesep)
                file.write("\\newcommand{\\WETRANSFERBOOL}{" + wetransferbool + "}" + os.linesep)
                file.write("\\newcommand{\\TEAMBOOL}{" + teambool + "}" + os.linesep)
                file.write("\\newcommand{\\OTRABOOL}{" + otrabool + "}" + os.linesep)

                file.write("\\newcommand{\\OTRABOOLdos}{" + otrabool2 + "}" + os.linesep)
                file.write("\\newcommand{\\OTRABOOLtres}{" + otrabool3 + "}" + os.linesep)
                file.write("\\newcommand{\\OTRABOOLcuatro}{" + otrabool4 + "}" + os.linesep)

                file.write("\\newcommand{\\URLDESCARGA}{"+ validated_data.get('urlDescarga') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLFOROS}{"+ validated_data.get('urlForos') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLREDES}{"+ validated_data.get('urlRedes') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLCOMERCIO}{"+ validated_data.get('urlComercio') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLVIDEOS}{"+ validated_data.get('urlVideos') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLWHATS}{"+ validated_data.get('urlWhats') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLDROPBOX}{"+ validated_data.get('urlDropbox') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLONEDRIVE}{"+ validated_data.get('urlOnedrive') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLSKYPE}{"+ validated_data.get('urlSkype') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLWETRANSFER}{"+ validated_data.get('urlWetransfer') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLTEAM}{"+ validated_data.get('urlTeam') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLOTRA}{"+ validated_data.get('urlOtra') + "}"+ os.linesep)

                file.write("\\newcommand{\\URLOTRAdos}{"+ validated_data.get('urlOtra2') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLOTRAtres}{"+ validated_data.get('urlOtra3') + "}"+ os.linesep)
                file.write("\\newcommand{\\URLOTRAcuatro}{"+ validated_data.get('urlOtra4') + "}"+ os.linesep)


                file.write("\\newcommand{\\JUSTIFICADESCARGA}{"+ validated_data.get('justificaDescarga') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAFOROS}{"+ validated_data.get('justificaForos') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAREDES}{"+ validated_data.get('justificaRedes') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICACOMERCIO}{"+ validated_data.get('justificaComercio') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAVIDEOS}{"+ validated_data.get('justificaVideos') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAWHATS}{"+ validated_data.get('justificaWhats') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICADROPBOX}{"+ validated_data.get('justificaDropbox') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAONEDRIVE}{"+ validated_data.get('justificaOnedrive') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICASKYPE}{"+ validated_data.get('justificaSkype') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAWETRANSFER}{"+ validated_data.get('justificaWetransfer') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICATEAM}{"+ validated_data.get('justificaTeam') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAOTRA}{"+ validated_data.get('justificaOtra') + "}"+ os.linesep)

                file.write("\\newcommand{\\JUSTIFICAOTRAdos}{"+ validated_data.get('justificaOtra2') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAOTRAtres}{"+ validated_data.get('justificaOtra3') + "}"+ os.linesep)
                file.write("\\newcommand{\\JUSTIFICAOTRAcuatro}{"+ validated_data.get('justificaOtra4') + "}"+ os.linesep)

                file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)##PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----


            # Preparar archivos en el directorio temporal
            archivo_tex = os.path.join(temp_dir, "Formato_INTERNET.tex")
            nombre_pdf = os.path.join(temp_dir, "Formato_INTERNET.pdf")

            # Copia Formato_VPN_241105.tex del directorio /app/data al directorio temporal
            shutil.copy("/app/latex/Formato_INTERNET.tex", archivo_tex)

            # Copiar imágenes al directorio temporal
            imagenes_dir = os.path.join(temp_dir, "imagenes")
            shutil.copytree("/app/latex/imagenes", imagenes_dir)

            # Compilar latex Aux
            try:
                subprocess.run(['latex',  "-output-directory",  temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo .aux generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando archivo .aux: {e}")
                return jsonify({"error": f"Error al compilar LaTeX Aux: {e}"}), 500

            # Compilar latex PDF
            try:
                subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
                self.logger.info(f"Archivo PDF generado para {archivo_tex}")
            except:
                self.logger.error(f"Error generando PDF: {e}")
                return jsonify({"error": f"Error al compilar LaTeX PDF: {e}"}), 500
            
            # Cargar pdf
            output = BytesIO()
            with open(nombre_pdf, "rb") as pdf_file:
                output.write(pdf_file.read())
            output.seek(0)

            # Enviar archivo
            return send_file(
                output,
                mimetype="application/pdf",
                download_name="RegistroInternet.pdf",
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
            #shutil.rmtree(temp_dir)
            print("hola")

    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200
    
    