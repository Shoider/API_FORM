import subprocess
import pandas as pd
import tempfile
import shutil
import os
import re

from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from logger.logger import Logger
from marshmallow import ValidationError

class FileGeneratorRoute(Blueprint):
    """Class to handle the routes for file generation"""

    def __init__(self, service, forms_schema):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.forms_schema = forms_schema #ESQUEMA NUEVO
        self.service = service
        self.register_routes()

    def register_routes(self):
        """Function to register the routes for file generation"""
        self.route("/api/v1/vpn", methods=["POST"])(self.vpn)
        self.route("/api/v3/vpn", methods=["POST"])(self.vpnmayo)
        self.route("/api/v3/telefonia", methods=["POST"])(self.tel)
        self.route("/api/v3/rfc", methods=["POST"])(self.rfc)
        self.route("/api/v3/internet", methods=["POST"])(self.inter)
        self.route("/api/v3/dns", methods=["POST"])(self.dns)
        self.route("/api/healthcheck", methods=["GET"])(self.healthcheck)

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
    
    def crear_csv_desde_registros(self, temp_dir, nombre_archivo_csv, registros, Alta):
        """
        Crea un archivo CSV desde registros, asegurando que todas las columnas requeridas estén presentes.

        Args:
            temp_dir (str): Directorio temporal donde se guardará el CSV.
            nombre_archivo_csv (str): Nombre del archivo CSV a crear.
            registros (list): Array de diccionarios con los registros.
            Alta (bool): Indica si es un alta o no.
        """
        try:
            out_csv_path = os.path.join(temp_dir, nombre_archivo_csv)
            
            # Columnas requeridas en el orden deseado
            columnas_requeridas = ['N', 'SO', 'FRO', 'IPO', 'SD', 'FRD', 'IPD', 'PRO', 'PUER']
            
            # Procesar cada registro
            contador = 0
            temporalidades = ""
            registros_procesados = []

            for registro in registros:
                registro_procesado = {}
                
                # Eliminar campo 'isNew' si existe
                registro.pop('isNew', None)
                
                # Procesar cada campo según sea necesario
                if "IPO" in registro:
                    #registro_procesado["IPO"] = registro["IPO"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                    registro_IPO= registro["IPO"]
                    registro_IPO_modificado="\\url{" + registro_IPO + "}"
                    registro_procesado["IPO"] = registro_IPO_modificado
                if "IPD" in registro:
                    #registro_procesado["IPD"] = registro["IPD"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                    registro_IPD=  registro["IPD"]
                    registro_IPD_modificado="\\url{" + registro_IPD + "}"
                    registro_procesado["IPD"] = registro_IPD_modificado
                if "PUER" in registro:
                    registro_procesado["PUER"] = registro["PUER"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                if "SO" in registro:
                    registro_procesado["SO"] = "~" + " "+ registro["SO"]
                if "SD" in registro:
                    registro_procesado["SD"] = "~" + " "+ registro["SD"]
                
                # Procesar temporalidad
                cambio = ""
                if "TEMPO" in registro:
                    if registro["TEMPO"] == "Temporal":
                        contador += 1
                        cambio = "T" + str(contador)
                        if "FECHA" in registro:
                            temporalidades += "T" + str(contador) + ": " + str(registro["FECHA"]) + "\\\\"
                    elif registro["TEMPO"] == "Permanente":
                        cambio = "P"
                
                # Procesar ID
                if "id" in registro:
                    registro_procesado["N"] = str(registro["id"]) + ("\\\\" + str(cambio) if Alta else "")
                
                # Añadir todos los campos posibles (aunque estén vacíos)
                for col in [ 'FRO', 'FRD', 'PRO']:
                    if col in registro:
                        registro_procesado[col] = registro[col]
                
                registros_procesados.append(registro_procesado)
            
            # Crear DataFrame asegurando todas las columnas
            df = pd.DataFrame(registros_procesados)
            
            # Asegurar que todas las columnas requeridas estén presentes
            for col in columnas_requeridas:
                if col not in df.columns:
                    df[col] = ""  # O podrías usar None o np.nan
            
            # Reordenar columnas según el orden requerido
            df = df[columnas_requeridas]
            
            # Guardar el CSV
            df.to_csv(out_csv_path, index=False, mode='x')
            
            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")
            return temporalidades

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}")
            return ""

    def crear_csv_VPN_Web(self, temp_dir, nombre_archivo_csv, registros):
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

            columnas = ['id', 'movimiento', 'nombreSistema', 'siglas', 'puertosServicios','url']
            for registro in registros:
                for col in columnas:
                    registro.setdefault(col, "")

            if not registros:
                df = pd.DataFrame([{}], columns=columnas)
            else:
                df = pd.DataFrame(registros)

            for registro in registros:
                registro.pop('isNew', None)
                if "url" in registro:
                    url = registro["url"]
                    # Reemplaza los caracteres específicos por su versión con "\"
                    url = url.replace("%", "\%").replace("#", "\#").replace("^^", "\^^")
                    url_modificada = "\\url{" + url + "}"
                    registro["url"] = url_modificada
                if "siglas" in registro:
                    siglas=registro["siglas"]
                    siglas_modificado = siglas.replace("%", "\%").replace("#", "\#").replace("^^", "\^^").replace("_","\_")
                    registro["siglas"] = siglas_modificado
                if "nombreSistema" in registro:
                    nombre_sistema=registro["nombreSistema"]
                    nombre_sistema_modificado = nombre_sistema.replace("%", "\%").replace("#", "\#").replace("^^", "\^^").replace("_","\_")
                    registro["nombreSistema"]=nombre_sistema_modificado

            df = pd.DataFrame(registros)
            df = df.rename(columns={'id': 'ID'})  # Siempre renombra 'id' a 'N'
            df = df.rename(columns={'movimiento': 'ABC'})
            df = df.rename(columns={'nombreSistema': 'SIST'})
            df = df.rename(columns={'siglas': 'SIGLAS'})
            df = df.rename(columns={'url': 'URL'})
            df = df.rename(columns={'puertosServicios': 'PUERTOS'})
            df.to_csv(out_csv_path, index=False, mode='x')

            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}")

    def crear_csv_VPN_Remoto(self, temp_dir, nombre_archivo_csv, registros):
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

            columnas = ['id', 'movimiento', 'nomenclatura', 'nombreSistema', 'direccion', 'sistemaOperativo']
            for registro in registros:
                registro.pop('isNew', None)
                for col in columnas:
                    registro.setdefault(col, "")

            if not registros:
                df = pd.DataFrame([{}], columns=columnas)
            else:
                df = pd.DataFrame(registros)           

            df = pd.DataFrame(registros)
            df = df.rename(columns={'id': 'ID'})  # Siempre renombra 'id' a 'N'
            df = df.rename(columns={'movimiento': 'ABC'})  
            df = df.rename(columns={'nomenclatura': 'NOMEN'})  
            df = df.rename(columns={'nombreSistema': 'NOMBRE'})  
            df = df.rename(columns={'direccion': 'IP'})  
            df = df.rename(columns={'sistemaOperativo': 'SO'})  
            df.to_csv(out_csv_path, index=False, mode='x')

            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}") 

    def crear_csv_VPN_WebCE(self, temp_dir, nombre_archivo_csv, registros):        
        try:
            out_csv_path = os.path.join(temp_dir, nombre_archivo_csv)
            columnas = ['IDU', 'NOMBRE', 'SIGLAS', 'URL', 'PUERTOS']
            for registro in registros:
                registro.pop('isNew', None)
                for col in columnas:
                    registro.setdefault(col, "")

            if not registros:
                df = pd.DataFrame([{}], columns=columnas)
            else:
                df = pd.DataFrame(registros)

            for registro in registros:
                registro.pop('isNew', None)
                if "URL" in registro:
                    url = registro["URL"] 
                    # Reemplaza los caracteres específicos por su versión con "\"
                    url = url.replace("%", "\%").replace("#", "\#").replace("^^", "\^^")                   
                    url_modificada = "\\url{" + url + "}"
                    registro["URL"] = url_modificada
                if "SIGLAS" in registro:  
                    siglas =registro["SIGLAS"]   
                    siglas_modificada=siglas.replace("%", "\%").replace("#", "\#").replace("^^", "\^^").replace("_","\_")
                    registro["SIGLAS"]=siglas_modificada
                if "NOMBRE" in registro:
                    nombre_sistema= registro["NOMBRE"]
                    nombre_sistema_modificado=nombre_sistema.replace("%", "\%").replace("#", "\#").replace("^^", "\^^").replace("_","\_")
                    registro["NOMBRE"]=nombre_sistema_modificado       

            df = pd.DataFrame(registros)
            #df = df.rename(columns={'id': 'IDU'})  # Siempre renombra 'id' a 'N'
             
            df.to_csv(out_csv_path, index=False, mode='x')

            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}") 

    def crear_csv_VPN_Personal(self, temp_dir, nombre_archivo_csv, registros):        
        try:
            out_csv_path = os.path.join(temp_dir, nombre_archivo_csv)
            columnas = ['id', 'NOMBRE', 'CORREO', 'EMPRESA', 'EQUIPO', 'SERVICIOS']
            for registro in registros:
                registro.pop('isNew', None)
                for col in columnas:
                    registro.setdefault(col, "")

            if not registros:
                df = pd.DataFrame([{}], columns=columnas)
            else:
                df = pd.DataFrame(registros)
            
            for registro in registros:
                registro.pop('isNew', None)
                if "CORREO" in registro:
                    #Agrega un salto de línea en cada renglón
                    #Para CORREO
                    sistema=registro["CORREO"]
                    sistema_modificado = '\\\\'.join([sistema[i:i+20] for i in range(0, len(sistema), 20)]) #cada 1
                    registro["CORREO"] = sistema_modificado

            df = pd.DataFrame(registros)
            df = df.rename(columns={'id': 'IDU'})  # Siempre renombra 'id' a 'N'
             
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

            # Guardar en BD
            new_vpn_data = validated_data
            vpn_registro, status_code = self.service.add_VPN(new_vpn_data)

            if status_code == 201:
                noformato = vpn_registro.get('_id')
                self.logger.info(f"Registro VPN agregado con ID: {noformato}")
            
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

                    # PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----
                    file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)

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
        
            else:
                return jsonify(vpn_registro), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "Detalles": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)

    def vpnmayo(self):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            # Validacion
            validated_data = self.forms_schema.load(data)
            self.logger.info("Ya se validaron correctamente")

            # Hacemos la busqueda en la base de datos para tener los registros
            datosRegistro, status_code = self.service.obtener_datos_por_id('vpnMayo', validated_data.get('id'))

            self.logger.info(f"Datos obtenidos de Mongo {datosRegistro}")

            if status_code == 201:
            
                # Transformar valores "SI" y "NO"
                altausuario = "x" if datosRegistro.get('movimiento', '~') == "ALTA" else " "
                bajausuario = "x" if datosRegistro.get('movimiento', '~') == "BAJA" else " "

                # Tipo de solicitante booleano. Esto es para que puedas manejar las tablas de la opcion 2
                conagua = "true" if datosRegistro.get('solicitante' , '~') == "CONAGUA" else "false"

                #Caso especial grupal
                casoespecialgrupal = "true" if datosRegistro.get('casoespecial' , '~') == "Grupal" else "false"

                # PARA BOOLEANOS DE FIRMA
                conaguafirma = "true" if datosRegistro.get('solicitante', '~') == "EXTERNO" else "false"
                sistemas = "true" if datosRegistro.get('subgerencia', '~')== "Subgerencia de Sistemas"  else "false"
                otrasub = "true" if sistemas == "false" else "false"

                # Opcion seleccionada
                cuentaUsuario = "true" if datosRegistro.get('cuentaUsuario') == True else "false"
                accesoWeb = "true" if datosRegistro.get('accesoWeb') == True else "false"
                accesoRemoto = "true" if datosRegistro.get('accesoRemoto') == True else "false"

                nombreusuario= datosRegistro.get('nombreInterno', '~') if conagua == "true" else datosRegistro.get('nombreExterno', '~')
                puestousuario= datosRegistro.get('puestoInterno', '~') if conagua == "true" else ""

                # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "DatosVPN.txt")
                with open(datos_txt_path, 'w') as file: 
                    file.write("\\newcommand{\\UA}{"+ datosRegistro.get('unidadAdministrativa', '~')+"}"+ os.linesep)
                    # PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----
                    file.write("\\newcommand{\\NOFORMATO}{" + datosRegistro.get('_id', '~') + "}" + os.linesep)

                    file.write("\\newcommand{\\JUSTIFICACION}{"+ datosRegistro.get('justificacion', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMEMO}{"+ datosRegistro.get('memorando', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\FECHA}{"+ datosRegistro.get('fecha', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\AREA}{"+ datosRegistro.get('areaAdscripcion', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\SUBGERENCIA}{"+ datosRegistro.get('subgerencia', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREENLACE}{"+ datosRegistro.get('nombreEnlace', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOENLACE}{"+ datosRegistro.get('puestoEnlace', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTENLACE}{"+ datosRegistro.get('telefonoEnlace', '~')+"}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBRECONAGUA}{"+ datosRegistro.get('nombreInterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOCONAGUA}{"+ datosRegistro.get('puestoInterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOCONAGUA}{"+ datosRegistro.get('correoInterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTCONAGUA}{"+ datosRegistro.get('telefonoInterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEXTERNO}{"+ datosRegistro.get('nombreExterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOEXTERNO}{"+ datosRegistro.get('correoExterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEMPRESA}{"+ datosRegistro.get('empresaExterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EQUIPODES}{"+ datosRegistro.get('equipoExterno', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOEMPLEADO}{"+ datosRegistro.get('numeroEmpleadoResponsable', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEMPLEADO}{"+ datosRegistro.get('nombreResponsable', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOEMPLEADO}{"+ datosRegistro.get('puestoResponsable', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\UAEMPLEADO}{"+ datosRegistro.get('unidadAdministrativaResponsable', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTEMPLEADO}{"+ datosRegistro.get('telefonoResponsable', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\TIPOEQUIPO}{"+ datosRegistro.get('tipoEquipo', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\SO}{"+ datosRegistro.get('sistemaOperativo', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\VERSIONSO}{"+ datosRegistro.get('versionSO', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\MARCA}{"+ datosRegistro.get('marca', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\MODELO}{"+ datosRegistro.get('modelo', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOSERIE}{"+ datosRegistro.get('serie', '~')+"}"+ os.linesep)

                    file.write("\\newcommand{\\ALTAUSUARIO}{" + altausuario + "}" + os.linesep)
                    file.write("\\newcommand{\\BAJAUSUARIO}{" + bajausuario + "}" + os.linesep)

                    file.write("\\newcommand{\\NOMBREUSUARIO}{"+ nombreusuario+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOUSUARIO}{"+ puestousuario+"}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBREJEFE}{"+ datosRegistro.get('nombreAutoriza', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOJEFE}{"+ datosRegistro.get('puestoAutoriza', '~')+"}"+ os.linesep)

                    # Booleanos para las opciones necesarias de mostrar tablas o no
                    file.write("\\newcommand{\\CONAGUA}{" + conagua + "}" + os.linesep)

                    file.write("\\newcommand{\\CUENTAUSUARIO}{" + cuentaUsuario + "}" + os.linesep)
                    file.write("\\newcommand{\\ACCESOWEB}{" + accesoWeb + "}" + os.linesep)
                    file.write("\\newcommand{\\ACCESOREMOTO}{" + accesoRemoto + "}" + os.linesep)

                    ##BOOLEANOS PARA FIRMAS 
                    file.write("\\newcommand{\\CONAGUAFIRMA}{" + conaguafirma + "}" + os.linesep)
                    file.write("\\newcommand{\\SISTEMAS}{" + sistemas + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRA}{" + otrasub + "}" + os.linesep)

                    file.write("\\newcommand{\\CASOESPECIALGRUPAL}{" + casoespecialgrupal + "}" + os.linesep)


                # Archivos .csv para las tablas
                # b) Acceso a sitios Web
                registros = datosRegistro.get('registrosWeb', [])       # Obtiene array de los datos
                self.crear_csv_VPN_Web(temp_dir, "SITIOSWEB.csv", registros)   # Se crea el .csv

                # c) Acceso a escritorio remoto
                registros = datosRegistro.get('registrosRemoto', []) 
                self.crear_csv_VPN_Remoto(temp_dir, "REMOTOESC.csv", registros)

                #Relación de personal externo (Caso de Subgerencia de Sistemas)
                registros = datosRegistro.get('registrosPersonal', [])       # Obtiene array de los datos
                self.crear_csv_VPN_Personal(temp_dir, "PERSONAL.csv", registros)   # Se crea el .csv

                #Servicios solicitado (Caso de Subgerencia de Sistemas)
                registros = datosRegistro.get('registrosWebCE', [])       # Obtiene array de los datos
                self.crear_csv_VPN_WebCE(temp_dir, "SITIOSWEBCE.csv", registros)   # Se crea el .csv               

                # Preparar archivos en el directorio temporal
                archivo_tex = os.path.join(temp_dir, "Formato_VPN_Mayo.tex")
                nombre_pdf = os.path.join(temp_dir, "Formato_VPN_Mayo.pdf")

                # Copia Formato_VPN_Mayo.tex del directorio /app/data al directorio temporal
                shutil.copy("/app/latex/Formato_VPN_Mayo.tex", archivo_tex)

                # Copiar imágenes al directorio temporal
                imagenes_dir = os.path.join(temp_dir, "imagenes")
                shutil.copytree("/app/latex/imagenes", imagenes_dir)

                # Compilar XeLaTeX
                try:
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                except:
                    self.logger.error(f"Error generando PDF: {e}")                    
                    return jsonify({"error": f"Error al compilar XeTex PDF: {e}"}), 500
                
                # Cargar pdf
                output = BytesIO()
                with open(nombre_pdf, "rb") as pdf_file:
                    output.write(pdf_file.read())
                output.seek(0)

                # Enviar archivo
                return send_file(
                    output,
                    mimetype="application/pdf",
                    download_name="Registro_VPN_Mayo.pdf",
                    as_attachment=True,
                )
        
            else:
                return jsonify(datosRegistro), status_code

        except ValidationError as err:
            self.logger.error("Ocurrieron errores de validación")
            self.logger.error(f"Errores de validación completos: {err.messages}")
            return jsonify({"error": "Datos invalidos", "message": err.messages}), 422
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            noformato = datosRegistro.get('_id')
            self.service.borrar_registro(noformato,"vpnMayo")
            self.service.borrar_contador(noformato,"vpnMayoCounters")
            self.service.registrar_error("VPN", "Error al compilar XeLaTeX")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)  
            #self.logger.info(f"Directorio temporal: {temp_dir}")        

    def tel(self):
        try:

            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            # Validacion
            validated_data = self.forms_schema.load(data)
            self.logger.info("Ya se validaron correctamente")

            # Hacemos la busqueda en la base de datos para tener los registros
            datosRegistro, status_code = self.service.obtener_datos_por_id('tel', validated_data.get('id'))

            if status_code == 201:
                noformato = datosRegistro.get('_id', ' ')
                self.logger.info(f"Registro TELEFONIA agregado con ID: {noformato}")
            
                # Tipo de Movimiento
                alta = "X" if datosRegistro.get('movimiento') == "ALTA" else " "
                movbaja = "true" if datosRegistro.get('movimiento') == "BAJA" else "false"
                movcambio = "true" if datosRegistro.get('movimiento') == "CAMBIO" else "false"
                baja = "X" if datosRegistro.get('movimiento') == "BAJA" else " "
                cambio = "X" if datosRegistro.get('movimiento') == "CAMBIO" else " "

                # Direccion
                direcion = datosRegistro.get('direccion', ' ') + ", " + datosRegistro.get('piso', ' ') + ", " + datosRegistro.get('ala', ' ')

                # Traducir valores true y false #PENDIGN
                externo= "true" if datosRegistro.get('tipoUsuario') == "Externo" else "false"
                
                # Transformar valores "X" y " "
                siMundo = "X" if datosRegistro.get('mundo') == "SI" else " "
                noMundo = "X" if datosRegistro.get('mundo') == "NO" else " "                
                siNacional = "X" if datosRegistro.get('nacional') == "SI" else " "
                noNacional = "X" if datosRegistro.get('nacional') == "NO" else " "
                siCelular = "X" if datosRegistro.get('celular') == "SI" else " "
                noCelular = "X" if datosRegistro.get('celular') == "NO" else " "

                # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "Datos.txt")
                
                with open(datos_txt_path, 'w') as file: 
                    file.write("\\newcommand{\\ALTA}{" + alta + "}" + os.linesep)
                    file.write("\\newcommand{\\BAJA}{" + baja + "}" + os.linesep)
                    file.write("\\newcommand{\\CAMBIO}{" + cambio + "}" + os.linesep)

                    file.write("\\newcommand{\\TIPOUSUARIO}{"+ datosRegistro.get('tipoUsuario', ' ')+"}"+ os.linesep)

                    file.write("\\newcommand{\\ACTIVACION}{"+ datosRegistro.get('activacion', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXPIRACION}{" + datosRegistro.get('expiracion', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREUSUARIO}{" + datosRegistro.get('nombreUsuario', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOUSUARIO}{" + datosRegistro.get('correoUsuario', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\DIRECCION}{" + direcion + "}"+ os.linesep)
                    file.write("\\newcommand{\\UAUSUARIO}{" + datosRegistro.get('uaUsuario', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEMPLEADO}{" + datosRegistro.get('nombreEmpleado', ' ')+ "}"+ os.linesep)
                    file.write("\\newcommand{\\IDEMPLEADO}{" + datosRegistro.get('idEmpleado', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXTEMPLEADO}{" + datosRegistro.get('extEmpleado', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOEMPLEADO}{"+ datosRegistro.get('correoEmpleado', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOEMPLEADO}{"+ datosRegistro.get('puestoEmpleado', ' ') + "}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBREENLACE}{"+ datosRegistro.get('nombreEnlace', ' ') + "}"+ os.linesep)

                    file.write("\\newcommand{\\EXTINTERNO}{" + datosRegistro.get('extinterno', ' ') + "}"+ os.linesep)


                    file.write("\\newcommand{\\SIMUNDO}{" + siMundo + "}" + os.linesep)
                    file.write("\\newcommand{\\NOMUNDO}{" + noMundo + "}" + os.linesep)
                    file.write("\\newcommand{\\SICELULAR}{" + siCelular + "}" + os.linesep)
                    file.write("\\newcommand{\\NOCELULAR}{" + noCelular + "}" + os.linesep)
                    file.write("\\newcommand{\\SINACIONAL}{" + siNacional + "}" + os.linesep)
                    file.write("\\newcommand{\\NONACIONAL}{" + noNacional + "}" + os.linesep)
                    
                    file.write("\\newcommand{\\JUSTIFICACION}{"+ datosRegistro.get('justificacion', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOUSUARIO}{"+ datosRegistro.get('puestoUsuario', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREJEFE}{" + datosRegistro.get('nombreJefe', ' ') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOJEFE}{" + datosRegistro.get('puestoJefe', ' ') + "}"+ os.linesep) 

                    file.write("\\newcommand{\\EXTERNO}{" + externo + "}" + os.linesep)
                    file.write("\\newcommand{\\MARCA}{" + datosRegistro.get('marca', ' ') + "}" + os.linesep)
                    file.write("\\newcommand{\\MODELO}{" + datosRegistro.get('modelo', ' ') + "}" + os.linesep)
                    file.write("\\newcommand{\\SERIE}{" + datosRegistro.get('serie', ' ') + "}" + os.linesep)
                    #file.write("\\newcommand{\\VERSION}{" + datosRegistro.get('version', ' ') + "}" + os.linesep)
                    file.write("\\newcommand{\\MOVBAJA}{" + movbaja + "}" + os.linesep)
                    file.write("\\newcommand{\\MOVCAMBIO}{" + movcambio + "}" + os.linesep)

                    file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)

                # Preparar archivos en el directorio temporal
                archivo_tex = os.path.join(temp_dir, "Formato_TELEFONIA.tex")
                nombre_pdf = os.path.join(temp_dir, "Formato_TELEFONIA.pdf")

                # Copia Formato_TELEFONIA.tex del directorio /app/data al directorio temporal
                shutil.copy("/app/latex/Formato_TELEFONIA.tex", archivo_tex)

                # Copiar imágenes al directorio temporal
                imagenes_dir = os.path.join(temp_dir, "imagenes")
                shutil.copytree("/app/latex/imagenes", imagenes_dir)

                # Compilar XeLaTeX
                try:
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                except:
                    self.logger.error(f"Error generando PDF: {e}")
                    return jsonify({"error": f"Error al compilar XeLaTeX: {e}"}), 500
                
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
            
            else:
                return jsonify(datosRegistro), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF")
            noformato = datosRegistro.get('_id')
            self.service.borrar_registro(noformato,"tel")
            self.service.borrar_contador(noformato,"telCounters")
            self.service.registrar_error("Telefonia", "Error al compilar XeLaTeX")
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
            validated_data = self.forms_schema.load(data)
            self.logger.info("Ya se validaron correctamente")

            # Hacemos la busqueda en la base de datos para tener los registros
            datosRegistro, status_code = self.service.obtener_datos_por_id('rfc', validated_data.get('id'))

            if status_code == 201:    

                # Booleanos para   Quien solicita
                if (datosRegistro.get('region') == "central"):
                    #solicitante = "true"
                    enlacein = "false"
                else:
                    #solicitante = "true"
                    enlacein = "true"
                
                ##IF DE PRUEBA
                enlacein = "true" if datosRegistro.get ('region') == 'regional' else "false"
                #enlacesolibool = "true" if solicitante == "true" and enlacein == "true" else "false"
                #solicitantebool = "true" if solicitante == "true" and enlacesolibool == "false" else "false"
                #enlaceinbool = "true" if enlacein == "true" and enlacesolibool == "false" else "false"

                # Transformar valores "X" y " " para Tipo de Movimiento
                intersistemas = "x" if datosRegistro.get('intersistemas') == True else " "
                administrador = "x" if datosRegistro.get('administrador') == True else " "
                desarrollador = "x" if datosRegistro.get('desarrollador') == True else " "
                usuario = "x" if datosRegistro.get('usuario') == True else " "
                otro = "x" if datosRegistro.get('otro') == True else " "

                # Booleanos para Tipo de Movimiento
                intersistemasBool = "true" if datosRegistro.get('intersistemas') == True else "false"
                administradorBool = "true" if datosRegistro.get('administrador') == True else "false"
                desarrolladorBool = "true" if datosRegistro.get('desarrollador') == True else "false"
                usuarioBool = "true" if datosRegistro.get('usuario') == True else "false"
                otroBool = "true" if datosRegistro.get('otro') == True else "false"

                # Booleanos para Generacion de tablas
                AltaInter = "true" if datosRegistro.get('AltaInter') == True else "false"
                BajaInter = "true" if datosRegistro.get('BajaInter') == True else "false"
                AltaAdmin = "true" if datosRegistro.get('AltaAdmin') == True else "false"
                BajaAdmin = "true" if datosRegistro.get('BajaAdmin') == True else "false"
                AltaDes = "true" if datosRegistro.get('AltaDes') == True else "false"
                BajaDes = "true" if datosRegistro.get('BajaDes') == True else "false"
                AltaUsua = "true" if datosRegistro.get('AltaUsua') == True else "false"
                BajaUsua = "true" if datosRegistro.get('BajaUsua') == True else "false"
                AltaOtro = "true" if datosRegistro.get('AltaOtro') == True else "false"
                BajaOtro = "true" if datosRegistro.get('BajaOtro') == True else "false"

                # En caso de cambios
                if datosRegistro.get('CambioInter') == True:
                    AltaInter = "true"
                    BajaInter = "true"
                if datosRegistro.get('CambioAdmin') == True:
                    AltaAdmin = "true"
                    BajaAdmin = "true"
                if datosRegistro.get('CambioDes') == True:
                    AltaDes = "true"
                    BajaDes = "true"
                if datosRegistro.get('CambioUsua') == True:
                    AltaUsua = "true"
                    BajaUsua = "true"
                if datosRegistro.get('CambioOtro') == True:
                    AltaOtro = "true"
                    BajaOtro = "true"

                # Desotro valor default
                desotro_value = datosRegistro.get('desotro', '')

                # Unir Justificaciones
                justifica1 = datosRegistro.get('justifica', '')
                justifica2 = datosRegistro.get('justifica2', '')
                justifica3 = datosRegistro.get('justifica3', '')

                # Validar si hay temporales
                if (justifica1 != ""): 
                    justEsp1 = "\\\\"
                else:
                    justEsp1 = ""

                if (justifica2 != ""): 
                    justEsp2 = "\\\\"
                else:
                    justEsp2 = ""

                # Concatenar con espacios y saltos de linea
                justifica_combined = justifica1 + justEsp1 + justifica2 + justEsp2 + justifica3  

                # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "Datos.txt")
                with open(datos_txt_path, 'w') as file: 
                   # file.write("\\newcommand{\\SOLI}{" + solicitante + "}" + os.linesep)
                    file.write("\\newcommand{\\ENLACE}{" + enlacein + "}" + os.linesep)

                    file.write("\\newcommand{\\REGIONAL}{" + enlacein + "}" + os.linesep)

                    #file.write("\\newcommand{\\ENLACESOLIBOOL}{" + enlacesolibool + "}" + os.linesep)
                    #file.write("\\newcommand{\\SOLIBOOL}{" + solicitantebool + "}" + os.linesep)
                    #file.write("\\newcommand{\\ENLACEBOOL}{" + enlaceinbool + "}" + os.linesep)

                    file.write("\\newcommand{\\FECHASOLI}{"+ datosRegistro.get('fecha', '~')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOTICKET}{"+ datosRegistro.get('noticket', '')+"}"+ os.linesep)
                    file.write("\\newcommand{\\MEMO}{"+ datosRegistro.get('memo', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\DESCBREVE}{" + datosRegistro.get('descbreve', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMEI}{"+ datosRegistro.get('nomei', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXTEI}{"+ datosRegistro.get('extei', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMS}{"+ datosRegistro.get('noms', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXTS}{" + datosRegistro.get('exts', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOS}{" + datosRegistro.get('puestos', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\AREAS}{" + datosRegistro.get('areas', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\DESDET}{" + datosRegistro.get('desdet', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICA}{" + justifica_combined + "}" + os.linesep)
                    file.write("\\newcommand{\\NOMBREJEFE}{" + datosRegistro.get('nombreJefe', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOJEFE}{" + datosRegistro.get('puestoJefe', '') + "}"+ os.linesep)

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

                    file.write("\\newcommand{\\NOFORMATO}{" + datosRegistro.get('_id', '') + "}" + os.linesep)

                # Tablas csv

                # Intersistemas
                # Cambios
                registrosAltas = datosRegistro.get('registrosInterCambiosAltas', [])  # Obtiene array de los datos
                registrosBajas = datosRegistro.get('registrosInterCambiosBajas', [])  # Obtiene array de los datos
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)            
                # Altas
                registros = datosRegistro.get('registrosInterAltas', [])   # Obtiene array de los datos
                registros.extend(registrosAltas)                            # Unir registros de altas y cambios
                tempInter = self.crear_csv_desde_registros(temp_dir, "ALTASINTER.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = datosRegistro.get('registrosInterBajas', [])   # Obtiene array de los datos
                registros.extend(registrosBajas)                            # Unir registros de bajas y cambios
                self.crear_csv_desde_registros(temp_dir, "BAJASINTER.csv", registros, False) #Se cambia el nombre de la columna

                # Administrador
                # Cambios
                registrosAltas = datosRegistro.get('registrosAdminCambiosAltas', [])
                registrosBajas = datosRegistro.get('registrosAdminCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = datosRegistro.get('registrosAdminAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas)      
                tempAdmin = self.crear_csv_desde_registros(temp_dir, "ALTASADMIN.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = datosRegistro.get('registrosAdminBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas)   
                self.crear_csv_desde_registros(temp_dir, "BAJASADMIN.csv", registros, False) #Se cambia el nombre de la columna

                # Desarrollador
                # Cambios
                registrosAltas = datosRegistro.get('registrosDesCambiosAltas', [])
                registrosBajas = datosRegistro.get('registrosDesCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = datosRegistro.get('registrosDesAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempDes = self.crear_csv_desde_registros(temp_dir, "ALTASDES.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = datosRegistro.get('registrosDesBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas) 
                self.crear_csv_desde_registros(temp_dir, "BAJASDES.csv", registros, False) #Se cambia el nombre de la columna

                # Usuario
                # Cambios
                registrosAltas = datosRegistro.get('registrosUsuaCambiosAltas', [])
                registrosBajas = datosRegistro.get('registrosUsuaCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = datosRegistro.get('registrosUsuaAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempUsua = self.crear_csv_desde_registros(temp_dir, "ALTASUSUA.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = datosRegistro.get('registrosUsuaBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas) 
                self.crear_csv_desde_registros(temp_dir, "BAJASUSUA.csv", registros, False) #Se cambia el nombre de la columna

                # Otro
                # Cambios
                registrosAltas = datosRegistro.get('registrosOtroCambiosAltas', [])
                registrosBajas = datosRegistro.get('registrosOtroCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = datosRegistro.get('registrosOtroAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempOtro = self.crear_csv_desde_registros(temp_dir, "ALTASOTRO.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = datosRegistro.get('registrosOtroBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas) 
                self.crear_csv_desde_registros(temp_dir, "BAJASOTRO.csv", registros, False) #Se cambia el nombre de la columna

                # Validar si hay temporales
                tempInterBool = tempInter != ""
                tempAdminBool = tempAdmin != ""
                tempDesBool = tempDes != ""
                tempUsuaBool = tempUsua != ""
                tempOtroBool = tempOtro != ""

                tempInterBool2 = "true" if tempInterBool == True else "false"
                tempAdminBool2 = "true" if tempAdminBool == True else "false"
                tempDesBool2 = "true" if tempDesBool == True else "false"
                tempUsuaBool2 = "true" if tempUsuaBool == True else "false"
                tempOtroBool2 = "true" if tempOtroBool == True else "false"

                # Temporalidades
                with open(datos_txt_path, 'a') as file: 
                    file.write("\\newcommand{\\TEMPOINTER}{"+ tempInter +"}"+ os.linesep)
                    file.write("\\newcommand{\\TEMPOUSUA}{"+ tempUsua +"}"+ os.linesep)
                    file.write("\\newcommand{\\TEMPOADMIN}{"+ tempAdmin +"}"+ os.linesep)
                    file.write("\\newcommand{\\TEMPODES}{"+ tempDes +"}"+ os.linesep)
                    file.write("\\newcommand{\\TEMPOOTRO}{"+ tempOtro +"}"+ os.linesep)
                    #Booleanos para Temporalidades
                    #file.write("\\newcommand{\\TEMPOINTERBOOL}{" + AltaInter + "}" + os.linesep)
                    #file.write("\\newcommand{\\TEMPOADMINBOOL}{" + AltaAdmin + "}" + os.linesep)
                    #file.write("\\newcommand{\\TEMPODESBOOL}{" + AltaDes + "}" + os.linesep)
                    #file.write("\\newcommand{\\TEMPOUSUABOOL}{" + AltaUsua + "}" + os.linesep)
                    #file.write("\\newcommand{\\TEMPOOTROBOOL}{" + AltaOtro + "}" + os.linesep)
                    #Booleanos para tabla de temporalidades
                    file.write("\\newcommand{\\HAYTEMPORALINTER}{" + tempInterBool2 + "}" + os.linesep)
                    file.write("\\newcommand{\\HAYTEMPORALADMIN}{" + tempAdminBool2 + "}" + os.linesep)
                    file.write("\\newcommand{\\HAYTEMPORALDES}{" + tempDesBool2 + "}" + os.linesep)
                    file.write("\\newcommand{\\HAYTEMPORALUSUA}{" + tempUsuaBool2 + "}" + os.linesep)
                    file.write("\\newcommand{\\HAYTEMPORALOTRO}{" + tempOtroBool2 + "}" + os.linesep)

                # Preparar archivos en el directorio temporal
                archivo_tex = os.path.join(temp_dir, "Formato_RFC_LT.tex")
                nombre_pdf = os.path.join(temp_dir, "Formato_RFC_LT.pdf")

                # Copia Formato_RFC_LT.tex del directorio /app/data al directorio temporal
                shutil.copy("/app/latex/Formato_RFC_LT.tex", archivo_tex)

                # Copiar imágenes al directorio temporal
                imagenes_dir = os.path.join(temp_dir, "imagenes")
                shutil.copytree("/app/latex/imagenes", imagenes_dir)

                # Compilar XeLaTeX
                try:
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                except:
                    self.logger.error(f"Error generando PDF: {e}")
                    return jsonify({"error": f"Error al compilar XeLaTeX: {e}"}), 500

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
            
            else:
                return jsonify(datosRegistro), status_code
            
        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            noformato = datosRegistro.get('_id')
            #self.logger.debug(f"Fallo en generacion de formato #{noformato}")
            self.service.borrar_registro(noformato,"rfc")
            #self.logger.debug(f"Fallo generando counter")
            self.service.borrar_contador(noformato,"rfcCounters")
            self.service.registrar_error("RFC", "Error al compilar XeLaTeX")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)

    def inter(self):

        try: 

            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            # Validacion
            validated_data = self.forms_schema.load(data)
            self.logger.info("Ya se validaron correctamente")

            # Hacemos la busqueda en la base de datos para tener los registros
            datosRegistro, status_code = self.service.obtener_datos_por_id('internet', validated_data.get('id'))

            if status_code == 201:
            
                # Transformar valores "SI" y "NO"
                cambio = "false" if datosRegistro.get('cambio') == "SI" else "true"
                almacenamiento = "x" if datosRegistro.get('almacenamiento') == True else " "
                blogs = "x" if datosRegistro.get('blogs') == True else " "
                shareware = "x" if datosRegistro.get('shareware') == True else " "
                redes = "x" if datosRegistro.get('redes') == True else " "
                transmision = "x" if datosRegistro.get('transmision') == True else " "
                
                otra = "x" if datosRegistro.get('otra') == True else " "
                otra2 = "x" if datosRegistro.get('otra2') == True else " "
                otra3 = "x" if datosRegistro.get('otra3') == True else " "
                otra4 = "x" if datosRegistro.get('otra4') == True else " "

                almacenamientobool = "true" if datosRegistro.get('almacenamiento') == True else "false"
                blogsbool = "true" if datosRegistro.get('blogs') == True else "false"
                sharewarebool = "true" if datosRegistro.get('shareware') == True else "false"
                redesbool = "true" if datosRegistro.get('redes') == True else "false"
                transmisionbool = "true" if datosRegistro.get('transmision') == True else "false"
                
                otrabool = "true" if datosRegistro.get('otra') == True else "false"
                otrabool2 = "true" if datosRegistro.get('otra2') == True else "false"
                otrabool3 = "true" if datosRegistro.get('otra3') == True else "false"
                otrabool4 = "true" if datosRegistro.get('otra4') == True else "false"

                direcConAla = datosRegistro.get("direccion", ' ') + ", "+ datosRegistro.get("piso", ' ') + ", " + datosRegistro.get("ala", ' ')

                # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "Datos.txt")
                with open(datos_txt_path, 'w') as file: 
                    file.write("\\newcommand{\\FECHASOLI}{"+ datosRegistro.get('fecha', '')+"}"+ os.linesep)
                    file.write("\\newcommand{\\UAUSUARIO}{"+ datosRegistro.get('uaUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\AREAUSUARIO}{"+ datosRegistro.get('areaUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREUSUARIO}{" + datosRegistro.get('nombreUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOUSUARIO}{" + datosRegistro.get('puestoUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOUSUARIO}{" + datosRegistro.get('correoUsuario', '')+ "}"+ os.linesep)
                    file.write("\\newcommand{\\TELUSUARIO}{" + datosRegistro.get('teleUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXTUSUARIO}{" + datosRegistro.get('extUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREJEFE}{"+ datosRegistro.get('nombreJefe', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOJEFE}{"+ datosRegistro.get('puestoJefe', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\DIRECCION}{"+ direcConAla +  "}"+ os.linesep)

                    file.write("\\newcommand{\\NOMEMO}{" + datosRegistro.get('memo', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOTICKET}{" + datosRegistro.get('noticket', '') + "}"+ os.linesep)
                    
                    file.write("\\newcommand{\\IPACTUAL}{" + cambio + "}"+ os.linesep)

                    file.write("\\newcommand{\\IPUSUARIO}{" + datosRegistro.get('ipUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\IPANTERIOR}{" + datosRegistro.get('ipAnterior', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\ALMACENAMIENTO}{" + almacenamiento + "}" + os.linesep)
                    file.write("\\newcommand{\\BLOGS}{" + blogs + "}" + os.linesep)
                    file.write("\\newcommand{\\SHAREWARE}{" + shareware + "}" + os.linesep)
                    file.write("\\newcommand{\\REDES}{" + redes + "}" + os.linesep)
                    file.write("\\newcommand{\\TRANSMISION}{" + transmision + "}" + os.linesep)
                    
                    file.write("\\newcommand{\\OTRA}{" + otra + "}" + os.linesep)

                    file.write("\\newcommand{\\OTRAdos}{" + otra2 + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRAtres}{" + otra3 + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRAcuatro}{" + otra4 + "}" + os.linesep)

                    file.write("\\newcommand{\\OTRAC}{"+ datosRegistro.get('otraC', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\OTRACdos}{"+ datosRegistro.get('otraC2', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\OTRACtres}{"+ datosRegistro.get('otraC3', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\OTRACcuatro}{"+ datosRegistro.get('otraC4', '') + "}"+ os.linesep)
                    
                    file.write("\\newcommand{\\ALMACENAMIENTOBOOL}{" + almacenamientobool + "}" + os.linesep)
                    file.write("\\newcommand{\\BLOGSBOOL}{" + blogsbool + "}" + os.linesep)
                    file.write("\\newcommand{\\SHAREWAREBOOL}{" + sharewarebool + "}" + os.linesep)
                    file.write("\\newcommand{\\REDESBOOL}{" + redesbool + "}" + os.linesep)
                    file.write("\\newcommand{\\TRANSMISIONBOOL}{" + transmisionbool + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRABOOL}{" + otrabool + "}" + os.linesep)

                    file.write("\\newcommand{\\OTRABOOLdos}{" + otrabool2 + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRABOOLtres}{" + otrabool3 + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRABOOLcuatro}{" + otrabool4 + "}" + os.linesep)

                    file.write("\\newcommand{\\URLOTRA}{"+ datosRegistro.get('urlOtra', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\URLOTRAdos}{"+ datosRegistro.get('urlOtra2', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\URLOTRAtres}{"+ datosRegistro.get('urlOtra3', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\URLOTRAcuatro}{"+ datosRegistro.get('urlOtra4', '') + "}"+ os.linesep)


                    file.write("\\newcommand{\\JUSTIFICAALMACENAMIENTO}{"+ datosRegistro.get('justificaAlmacenamiento', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICABLOGS}{"+ datosRegistro.get('justificaBlogs', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICAREDES}{"+ datosRegistro.get('justificaRedes', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICASHAREWARE}{"+ datosRegistro.get('justificaShareware', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICATRANSMISION}{"+ datosRegistro.get('justificaTransmision', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICAOTRA}{"+ datosRegistro.get('justificaOtra', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\JUSTIFICAOTRAdos}{"+ datosRegistro.get('justificaOtra2', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICAOTRAtres}{"+ datosRegistro.get('justificaOtra3', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICAOTRAcuatro}{"+ datosRegistro.get('justificaOtra4', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\NOFORMATO}{" + datosRegistro.get('_id', '') + "}" + os.linesep)

                # Preparar archivos en el directorio temporal
                archivo_tex = os.path.join(temp_dir, "Formato_INTERNET.tex")
                nombre_pdf = os.path.join(temp_dir, "Formato_INTERNET.pdf")

                # Copia Formato_VPN_241105.tex del directorio /app/data al directorio temporal
                shutil.copy("/app/latex/Formato_INTERNET.tex", archivo_tex)

                # Copiar imágenes al directorio temporal
                imagenes_dir = os.path.join(temp_dir, "imagenes")
                shutil.copytree("/app/latex/imagenes", imagenes_dir)

                 # Compilar XeLaTeX
                try:
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                except:
                    self.logger.error(f"Error generando PDF: {e}")
                    return jsonify({"error": f"Error al compilar XeLaTeX: {e}"}), 500
                
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
            
            else:
                return jsonify(datosRegistro), status_code
            
        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF")
            noformato = datosRegistro.get('_id')
            self.service.borrar_registro(noformato,"internet")
            self.service.borrar_contador(noformato,"internetCounters")
            self.service.registrar_error("Internet", "Error al compilar XeLaTeX")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)
    def dns(self):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            # Validacion
            validated_data = self.forms_schema.load(data)
            self.logger.info("Ya se validaron correctamente")
            
            # Hacemos la busqueda en la base de datos para tener los registros
            datosRegistro, status_code = self.service.obtener_datos_por_id('dns', validated_data.get('id'))

            if status_code == 201:
                noformato = datosRegistro.get('_id', ' ')
                self.logger.info(f"Registro DNS agregado con ID: {noformato}")
            
            # Tipo de Movimiento
                alta = "X" if datosRegistro.get('movimiento') == "ALTA" else " "
                baja = "X" if datosRegistro.get('movimiento') == "BAJA" else " "
                cambio = "X" if datosRegistro.get('movimiento') == "CAMBIO" else " "

            #Tipo de registro CNA o CONAGUA
                cna = "X" if datosRegistro.get('registro') == "CNA" else " "
                conagua = "X" if datosRegistro.get('registro') == "CONAGUA" else " "
            
            # Direccion
                direcion = datosRegistro.get('direccion', ' ') + ", " + datosRegistro.get('piso', ' ') + ", " + datosRegistro.get('ala', ' ')
            
            # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "Datos.txt")

                with open(datos_txt_path, 'w') as file: 
                    file.write("\\newcommand{\\NOFORMATO}{" + datosRegistro.get('_id', '') + "}" + os.linesep)

                    file.write("\\newcommand{\\FECHASOLICITUD}{"+ datosRegistro.get('fecha', '~')+"}"+ os.linesep)

                    file.write("\\newcommand{\\ALTA}{" + alta + "}" + os.linesep)
                    file.write("\\newcommand{\\BAJA}{" + baja + "}" + os.linesep)
                    file.write("\\newcommand{\\CAMBIO}{" + cambio + "}" + os.linesep)

                    file.write("\\newcommand{\\NOMBRERESPONSABLE}{" + datosRegistro.get('nombreResponsable', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTORESPONSABLE}{" + datosRegistro.get('puestoResponsable', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREUSUARIO}{" + datosRegistro.get('nombreUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\AREAUSUARIO}{" + datosRegistro.get('areaUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOUSUARIO}{" + datosRegistro.get('puestoUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\TELEFONOUSUARIO}{" + datosRegistro.get('telefonoUsuario', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\EXTUSUARIO}{" + datosRegistro.get('extUsuario', '') + "}"+ os.linesep)
                    
                    file.write("\\newcommand{\\CNA}{" + cna + "}" + os.linesep)
                    file.write("\\newcommand{\\CONAGUA}{" + conagua + "}" + os.linesep)

                    file.write("\\newcommand{\\NOMBREDNS}{" + datosRegistro.get('nombreRegistro', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\DIRIP}{" + datosRegistro.get('IP', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREAPLICACION}{" + datosRegistro.get('nombreAplicacion', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICACION}{" + datosRegistro.get('justificacion', '') + "}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBREAPROBA}{" + datosRegistro.get('nombreAproba', '') + "}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOAPROBA}{" + datosRegistro.get('puestoAproba', '') + "}"+ os.linesep)


            # Preparar archivos en el directorio temporal
                archivo_tex = os.path.join(temp_dir, "Formato_DNS.tex")
                nombre_pdf = os.path.join(temp_dir, "Formato_DNS.pdf")

                # Copia Formato_TELEFONIA.tex del directorio /app/data al directorio temporal
                shutil.copy("/app/latex/Formato_DNS.tex", archivo_tex)

                # Copiar imágenes al directorio temporal
                imagenes_dir = os.path.join(temp_dir, "imagenes")
                shutil.copytree("/app/latex/imagenes", imagenes_dir)
            # Compilar XeLaTeX
                try:
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    subprocess.run(["xelatex", "-output-directory", temp_dir, archivo_tex], check=True)
                    self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                except:
                    self.logger.error(f"Error generando PDF: {e}")
                    return jsonify({"error": f"Error al compilar XeLaTeX: {e}"}), 500
                
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
            
            else:
                return jsonify(datosRegistro), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF")
            noformato = datosRegistro.get('_id')
            #self.service.borrar_registro(noformato,"tel")
            #self.service.borrar_contador(noformato,"telCounters")
            #self.service.registrar_error("Telefonia", "Error al compilar XeLaTeX")
            return jsonify({"error": "Error generando PDF"}), 500
        #finally:
            # Eliminar el directorio temporal
            #shutil.rmtree(temp_dir)

    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200

