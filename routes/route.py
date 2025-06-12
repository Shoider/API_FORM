import subprocess
import pandas as pd
import tempfile
import shutil
import os
import datetime

from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from logger.logger import Logger
from marshmallow import ValidationError

class FileGeneratorRoute(Blueprint):
    """Class to handle the routes for file generation"""

    def __init__(self, service, forms_schemaVPN, forms_schemaVPNMayo, forms_schemaTel, forms_schemaRFC, forms_schemaInter, actualizarMemo, actualizarFuncionRol):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.forms_schemaVPN = forms_schemaVPN
        self.forms_schemaVPNMayo = forms_schemaVPNMayo
        self.forms_schemaTel = forms_schemaTel
        self.forms_schemaRFC = forms_schemaRFC
        self.forms_schemaInter = forms_schemaInter
        self.actualizarMemo = actualizarMemo
        self.actualizarFuncionRol = actualizarFuncionRol
        self.service = service
        self.register_routes()

    def register_routes(self):
        """Function to register the routes for file generation"""
        self.route("/api/v1/vpn", methods=["POST"])(self.vpn)
        self.route("/api/v2/vpn", methods=["POST"])(self.vpnmayo)
        self.route("/api/v2/vpnActualizar", methods=["POST"])(self.vpnMemorando)
        self.route("/api/v2/rfcActualizar", methods=["POST"])(self.rfcFuncionORol)
        self.route("/api/v1/tel", methods=["POST"])(self.tel)
        self.route("/api/v1/rfc", methods=["POST"])(self.rfc)
        self.route("/api/v1/inter", methods=["POST"])(self.inter)
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
        
    def eliminar_campos_vacios(self, datos):
        """
        Elimina recursivamente los campos (pares clave-valor) de los diccionarios
        donde el valor es una cadena vacía ("") ó ("null").

        Procesa diccionarios anidados y diccionarios dentro de listas.
        Las cadenas vacías que sean elementos directos de una lista (ej: ["a", "", "b"])
        NO se eliminan de la lista, ya que no son "campos" de un diccionario.
        Otros tipos de datos (números, booleanos, None, cadenas no vacías) se conservan.

        Args:
            datos: Puede ser un diccionario o una lista para limpiar.

        Returns:
            Una nueva estructura de datos (diccionario o lista) sin los campos
            que contenían cadenas vacías.
        """
        if isinstance(datos, dict):
            # Crear un nuevo diccionario para los datos limpios
            diccionario_limpio = {}
            for clave, valor in datos.items():
                if valor == "":
                    # Si el valor es una cadena vacía, omitir este campo
                    continue
                if valor == "null":
                    continue
                elif isinstance(valor, dict):
                    # Si el valor es un diccionario, aplicar la función recursivamente
                    diccionario_limpio[clave] = self.eliminar_campos_vacios(valor)
                elif isinstance(valor, list):
                    # Si el valor es una lista, aplicar la función recursivamente a cada elemento
                    diccionario_limpio[clave] = [self.eliminar_campos_vacios(item) for item in valor]
                else:
                    # Para cualquier otro valor, conservarlo
                    diccionario_limpio[clave] = valor
            return diccionario_limpio
        elif isinstance(datos, list):
            # Si la estructura de datos es una lista, aplicar la función a cada elemento
            return [self.eliminar_campos_vacios(item) for item in datos]
        else:
            # Si no es un diccionario ni una lista (ej: string, int, None), devolverlo tal cual
            return datos
        
    def crear_csv_desde_registros(self, temp_dir, nombre_archivo_csv, registros, Alta):
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

            contador = 0
            temporalidades = ""

            for registro in registros:
                registro.pop('isNew', None)
                if "IPO" in registro:
                    ip=registro["IPO"]
                    #ip_modificada = '\\\\'.join([ip[i:i+20] for i in range(0, len(ip), 20)])
                    #registro["IPO"] = ip_modificada
                    registro["IPO"] = registro["IPO"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                if "IPD" in registro:
                    ip=registro["IPD"]
                    #ip_modificada = '\\\\'.join([ip[i:i+20] for i in range(0, len(ip), 20)])
                    #registro["IPD"] = ip_modificada
                    registro["IPD"] = registro["IPD"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")
                #if "SO" in registro:
                 #   sistema=registro["SO"]
                    ##registro["SO"] = sistema_modificado
                    #registro["SO"] = registro["SO"].replace(" ", "\\\\").replace(", ", "\\\\")
                #if "SD" in registro:
                 #   sistema=registro["SD"]
                    #sistema_modificado = '\\\\'.join([sistema[i:i+8] for i in range(0, len(sistema), 8)])
                    #registro["SD"] = sistema_modificado
                    #registro["SD"] = registro["SD"].replace(" ", "\\\\").replace(", ", "\\\\")
                #if "FRO" in registro:
                 #   funcionrol=registro["FRO"]
                    #funcionrol_modificado = '\\\\'.join([funcionrol[i:i+10] for i in range(0, len(funcionrol), 10)])
                    #registro["FRO"] = funcionrol_modificado
                    #registro["FRO"] = registro["FRO"].replace(" ", "\\\\").replace(", ", "\\\\")
                #if "FRD" in registro:
                 #   funcionrol=registro["FRD"]
                    #funcionrol_modificado = '\\\\'.join([funcionrol[i:i+6] for i in range(0, len(funcionrol), 6)])
                    #registro["FRD"] = funcionrol_modificado
                    # registro["FRD"] = registro["FRD"].replace(" ", "\\\\").replace(", ", "\\\\")
                if "PUER" in registro:
                    #puertos=registro["PUER"]
                   # puertos_modificado = '\\\\'.join([puertos[i:i+5] for i in range(0, len(puertos), 5)])
                   # registro["PUER"] = puertos_modificado
                    registro["PUER"] = registro["PUER"].replace(" ", "\\\\").replace(", ", "\\\\").replace("/", "\\\\/")

                # TEMPORALIDAD
                cambio = ""  # Inicializa la variable cambio
                if "TEMPO" in registro:
                    if registro["TEMPO"] == "TEMPORAL":
                        contador = contador + 1
                        cambio = "T" + str(contador)
                        if "FECHA" in registro:
                            temporalidades += "T" + str(contador) + ": " + str(registro["FECHA"]) + "\\\\"
                    elif registro["TEMPO"] == "PERMANENTE":
                        cambio = "P"

                # Agrega el valor de cambio al campo "id"
                if Alta == True:
                    if "id" in registro:
                        registro["id"] = str(registro["id"]) + "\\\\" + str(cambio)

            df = pd.DataFrame(registros)
            df = df.rename(columns={'id': 'N'})  # Siempre renombra 'id' a 'N'
            df.to_csv(out_csv_path, index=False, mode='x')

            print(f"Archivo CSV '{nombre_archivo_csv}' creado exitosamente.")

            return temporalidades

        except Exception as e:
            print(f"Ocurrió un error al crear el archivo CSV: {e}")

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

            if not registros:
                df = pd.DataFrame([{}], columns=['id', 'movimiento', 'nombreSistema', 'siglas', 'url', 'puertosServicios'])

            #for registro in registros:
            #    registro.pop('isNew', None)
            #    if "nombreSistema" in registro:
                    ##AGREGA UN SALTO DE LINEA CADA XX CARÁCTERES PARA EVITAR LO QUE EL FORMATO DE LaTeX NO HACE
                    ##PARA nombresistema
            #        sistema=registro["nombreSistema"]
            #        sistema_modificado = '\\\\'.join([sistema[i:i+13] for i in range(0, len(sistema), 13)])
            #        registro["nombreSistema"] = sistema_modificado
            #    if "siglas" in registro:
                    ##PARA siglas
            #        siglas=registro["siglas"]
            #        siglas_modificado = '\\\\'.join([siglas[i:i+8] for i in range(0, len(siglas), 8)])
            #        registro["siglas"] = siglas_modificado
            #    if "url" in registro:
            #        ##PARA url
            #        url=registro["url"]
            #        url_modificada = '\\\\'.join([url[i:i+24] for i in range(0, len(url), 24)])
            #        registro["url"] = url_modificada
            #    if "puertosServicios" in registro:
            #        ##PARA puertos, aqui modifique para que fuera cada 3 caracteres 
            #        puertos=registro["puertosServicios"]
            #        puertos_modificado = '\\\\'.join([puertos[i:i+8] for i in range(0, len(puertos), 8)])
            #        registro["puertosServicios"] = puertos_modificado

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

            if not registros:
                df = pd.DataFrame([{}], columns=['id', 'movimiento', 'nomenclatura', 'nombreSistema', 'direccion', 'sistemaOperativo'])

            #for registro in registros:
            #    registro.pop('isNew', None)
            #    if "direccion" in registro:
                    ##AGREGA UN SALTO DE LINEA CADA XX CARÁCTERES PARA EVITAR LO QUE EL FORMATO DE LaTeX NO HACE
                    ##PARA DIRECCION
            #        direccion=registro["direccion"]
            #        direccion_modificada = '\\\\'.join([direccion[i:i+14] for i in range(0, len(direccion), 14)])
            #        registro["direccion"] = direccion_modificada
            #    if "nomenclatura" in registro:
                    ##NOMENCLATURA
            #        nomenclatura=registro["nomenclatura"]
            #        nomenclatura_modificada = '\\\\'.join([nomenclatura[i:i+14] for i in range(0, len(nomenclatura), 14)])
            #        registro["nomenclatura"] = nomenclatura_modificada
            #    if "nombreSistema" in registro:
                    ##NOMBRESISTEMA
            #        nombresistema=registro["nombreSistema"]
            #        nombresistema_modificado = '\\\\'.join([nombresistema[i:i+14] for i in range(0, len(nombresistema), 14)])
            #        registro["nombreSistema"] = nombresistema_modificado
            #    if "sistemaOperativo" in registro:
                    #SISTEMAOPERATIVO
            #        sistemaoperativo=registro["sistemaOperativo"]
            #        sistema_modificado = '\\\\'.join([sistemaoperativo[i:i+14] for i in range(0, len(sistemaoperativo), 14)])
            #        registro["sistemaOperativo"] = sistema_modificado
   

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


    def vpnmayo(self, data=None):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            if data is None:
                data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            datosParaValidacion = self.eliminar_campos_vacios(data)
            self.logger.info(f"Datos despues de limpieza: {datosParaValidacion}")
            self.forms_schemaVPNMayo.load(datosParaValidacion)
            self.logger.info("Ya se validaron correctamente")

            # Validacion
            validated_data = data
            
            # memorando NO viene o está vacío
            if not validated_data.get('memorando'):
                self.logger.info("El campo memorando está vacío o no fue enviado")
                # Guardar en BD
                new_vpnmayo_data = validated_data
                vpnmayo_registro, status_code = self.service.add_VPNMayo(new_vpnmayo_data)
                if status_code == 201:
                    noformato = vpnmayo_registro.get('_id')
                    self.logger.info(f"Registro VPN Mayo agregado con ID: {noformato}")
            else:
                self.logger.info("El campo memorando ya esta disponible")
                noformato=validated_data.get('_id')
                self.logger.info(f"Registro VPN Mayo actualizado con ID: {noformato}")
                self.logger.warning("No se actualizara la base de datos")
                status_code = 201

            if status_code == 201:
            
                # Transformar valores "SI" y "NO"
                altausuario = "x" if validated_data.get('movimiento') == "ALTA" else " "
                bajausuario = "x" if validated_data.get('movimiento') == "BAJA" else " "

                # Tipo de solicitante booleano. Esto es para que puedas manejar las tablas de la opcion 2
                conagua = "true" if validated_data.get('solicitante') == "CONAGUA" else "false"

                ###PARA BOOLEANOS DE FIRMA
                #conaguafirma = "true" if conagua == "true" else "false"
                conaguafirma = "true" if validated_data.get('solicitante') == "EXTERNO" else "false"
                sistemas = "true" if validated_data.get('subgerencia')== "Subgerencia de Sistemas"  else "false"
                otrasub = "true" if sistemas == "false" else "false"

                # Opcion seleccionada
                cuentaUsuario = "true" if validated_data.get('cuentaUsuario') == True else "false"
                accesoWeb = "true" if validated_data.get('accesoWeb') == True else "false"
                accesoRemoto = "true" if validated_data.get('accesoRemoto') == True else "false"

                nombreusuario= validated_data.get('nombreInterno') if conagua == "true" else validated_data.get('nombreExterno')
                puestousuario= validated_data.get('puestoInterno') if conagua == "true" else ""
                
                now = datetime.datetime.now()
                fecha = now.strftime("%d-%m-%Y")  # Formato: DD-MM-YYYY

                # Crear Datos.txt en el directorio temporal
                datos_txt_path = os.path.join(temp_dir, "DatosVPN.txt")
                with open(datos_txt_path, 'w') as file: 
                    file.write("\\newcommand{\\UA}{"+ validated_data.get('unidadAdministrativa')+"}"+ os.linesep)
                    file.write("\\newcommand{\\JUSTIFICACION}{"+ validated_data.get('justificacion')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMEMO}{"+ validated_data.get('memorando', ' ')+"}"+ os.linesep)
                    file.write("\\newcommand{\\FECHA}{"+ fecha +"}"+ os.linesep)
                    file.write("\\newcommand{\\AREA}{"+ validated_data.get('areaAdscripcion')+"}"+ os.linesep)
                    file.write("\\newcommand{\\SUBGERENCIA}{"+ validated_data.get('subgerencia')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREENLACE}{"+ validated_data.get('nombreEnlace')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTENLACE}{"+ validated_data.get('telefonoEnlace')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBRECONAGUA}{"+ validated_data.get('nombreInterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOCONAGUA}{"+ validated_data.get('puestoInterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOCONAGUA}{"+ validated_data.get('correoInterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTCONAGUA}{"+ validated_data.get('telefonoInterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEXTERNO}{"+ validated_data.get('nombreExterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\CORREOEXTERNO}{"+ validated_data.get('correoExterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEMPRESA}{"+ validated_data.get('empresaExterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EQUIPODES}{"+ validated_data.get('equipoExterno')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOEMPLEADO}{"+ validated_data.get('numeroEmpleadoResponsable')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOMBREEMPLEADO}{"+ validated_data.get('nombreResponsable')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOEMPLEADO}{"+ validated_data.get('puestoResponsable')+"}"+ os.linesep)
                    file.write("\\newcommand{\\UAEMPLEADO}{"+ validated_data.get('unidadAdministrativaResponsable')+"}"+ os.linesep)
                    file.write("\\newcommand{\\EXTEMPLEADO}{"+ validated_data.get('telefonoResponsable')+"}"+ os.linesep)
                    file.write("\\newcommand{\\TIPOEQUIPO}{"+ validated_data.get('tipoEquipo')+"}"+ os.linesep)
                    file.write("\\newcommand{\\SO}{"+ validated_data.get('sistemaOperativo')+"}"+ os.linesep)
                    file.write("\\newcommand{\\VERSIONSO}{"+ validated_data.get('versionSO')+"}"+ os.linesep)
                    file.write("\\newcommand{\\MARCA}{"+ validated_data.get('marca')+"}"+ os.linesep)
                    file.write("\\newcommand{\\MODELO}{"+ validated_data.get('modelo')+"}"+ os.linesep)
                    file.write("\\newcommand{\\NOSERIE}{"+ validated_data.get('serie')+"}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBREUSUARIO}{"+ nombreusuario+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOUSUARIO}{"+ puestousuario+"}"+ os.linesep)

                    file.write("\\newcommand{\\NOMBREJEFE}{"+ validated_data.get('nombreAutoriza')+"}"+ os.linesep)
                    file.write("\\newcommand{\\PUESTOJEFE}{"+ validated_data.get('puestoAutoriza')+"}"+ os.linesep)

                    file.write("\\newcommand{\\ALTAUSUARIO}{" + altausuario + "}" + os.linesep)
                    file.write("\\newcommand{\\BAJAUSUARIO}{" + bajausuario + "}" + os.linesep)

                    # Booleanos para las opciones necesarias de mostrar tablas o no
                    file.write("\\newcommand{\\CONAGUA}{" + conagua + "}" + os.linesep)

                    ##BOOLEANOS PARA FIRMAS 
                    file.write("\\newcommand{\\CONAGUAFIRMA}{" + conaguafirma + "}" + os.linesep)
                    file.write("\\newcommand{\\SISTEMAS}{" + sistemas + "}" + os.linesep)
                    file.write("\\newcommand{\\OTRA}{" + otrasub + "}" + os.linesep)

                    file.write("\\newcommand{\\CUENTAUSUARIO}{" + cuentaUsuario + "}" + os.linesep)
                    file.write("\\newcommand{\\ACCESOWEB}{" + accesoWeb + "}" + os.linesep)
                    file.write("\\newcommand{\\ACCESOREMOTO}{" + accesoRemoto + "}" + os.linesep)

                    # PARA AGREGAR NUMERO DE FORMATO EN TXT YYMMDD----
                    file.write("\\newcommand{\\NOFORMATO}{" + noformato + "}" + os.linesep)

                # Archivos .csv para las tablas
                # b) Acceso a sitios Web
                registros = validated_data.get('registrosWeb', [])       # Obtiene array de los datos
                self.crear_csv_VPN_Web(temp_dir, "SITIOSWEB.csv", registros)   # Se crea el .csv

                # c) Acceso a escritorio remoto
                registros = validated_data.get('registrosRemoto', []) 
                self.crear_csv_VPN_Remoto(temp_dir, "REMOTOESC.csv", registros)

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
                return jsonify(vpnmayo_registro), status_code

        except ValidationError as err:
            messages = err.messages
            self.logger.error("Ocurrieron errores de validación")
            self.logger.error(f"Errores de validación completos: {messages}")

            # CORREO INTERNO Y EXTERNO
            if 'correoInterno' in err.messages:
                self.logger.error(f"Error de validación: 'Correo interno invalido'")
                return jsonify({"message": "Datos invalidos"}), 205
            if 'correoExterno' in err.messages:
                self.logger.error(f"Error de validación: 'Correo externo invalido'")
                return jsonify({"message": "Datos invalidos"}), 207
            
            # TELEFONO ENLACE
            if 'telefonoEnlace' in err.messages:
                self.logger.error(f"Error de validación: 'teléfono enlace/contacto'")
                return jsonify({"message": "Datos invalidos"}), 206
            # TELEFONO INTERNO
            if 'telefonoInterno' in err.messages:
                self.logger.error(f"Error de validación: 'teléfono usuario CONAGUA'")
                return jsonify({"message": "Datos invalidos"}), 208
            # TELEFONO RESPONSABLE
            if 'telefonoResponsable' in err.messages:
                self.logger.error(f"Error de validación: 'teléfono usuario responsable'")
                return jsonify({"message": "Datos invalidos"}), 209
            
            # EMPLEADO RESPONSABLE
            if 'numeroEmpleadoResponsable' in err.messages:
                self.logger.error(f"Error de validación: 'número de empleado responsable'")
                return jsonify({"message": "Datos invalidos"}), 230

            # REGISTROS WEB B)
            if 'registrosWeb' in messages:
                web = messages['registrosWeb']
                if isinstance(web, dict):
                    for indice_item_str, errores_del_item in web.items():
                        # url
                        if isinstance(errores_del_item, dict) and 'url' in errores_del_item:
                            self.logger.error(f"Error de validación: 'url'")
                            return jsonify({"message": "Datos invalidos: 'url'"}), 210
                        # nombreSistema
                        if isinstance(errores_del_item, dict) and 'nombreSistema' in errores_del_item:
                            self.logger.error(f"Error de validación: 'nombreSistema'")
                            return jsonify({"message": "Datos invalidos: 'nombreSistema'"}), 211
            
            # REGISTROS REMOTO C)
            if 'registrosRemoto' in messages:
                remoto = messages['registrosRemoto']
                if isinstance(remoto, dict):
                    for indice_item_str, errores_del_item in remoto.items():
                        # nomeclatura
                        if isinstance(errores_del_item, dict) and 'nomenclatura' in errores_del_item:
                            self.logger.error(f"Error de validación: 'nomenclatura'")
                            return jsonify({"message": "Datos invalidos: 'nomenclatura'"}), 220
                        # nombreSistema
                        if isinstance(errores_del_item, dict) and 'nombreSistema' in errores_del_item:
                            self.logger.error(f"Error de validación: 'nombreSistema'")
                            return jsonify({"message": "Datos invalidos: 'nombreSistema'"}), 221
                        # direccion
                        if isinstance(errores_del_item, dict) and 'direccion' in errores_del_item:
                            self.logger.error(f"Error de validación: 'direccion'")
                            return jsonify({"message": "Datos invalidos: 'direccion'"}), 222
            
            # Otro error de validacion
            return jsonify({"error": "Datos invalidos", "Detalles": err.messages}), 422
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

            # Guardar en BD
            new_tel_data = validated_data
            tel_registro, status_code = self.service.add_tel(new_tel_data)

            if status_code == 201:
                noformato = tel_registro.get('_id')
                self.logger.info(f"Registro TELEFONIA agregado con ID: {noformato}")
            
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
                return jsonify(tel_registro), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)

    def rfc(self, data=None):
        try:
            # Crear directorio temporal único
            temp_dir = tempfile.mkdtemp()

            if data is None:
                data = request.get_json()

            if not data:
                return jsonify({"error": "Invalid data"}), 400

            # Validacion
            validated_data = self.forms_schemaRFC.load(data)    

            # memorando NO viene o está vacío
            if not validated_data.get('_id'):
                self.logger.info("El campo memorando está vacío o no fue enviado")
                # Guardar en BD
                new_rfc_data = validated_data
                rfc_registro, status_code = self.service.add_RFC(new_rfc_data)
                if status_code == 201:
                    noformato = rfc_registro.get('_id')
                    self.logger.info(f"Registro RFC agregado con ID: {noformato}")
            else:
                self.logger.info("El campo _id ya esta disponible")
                noformato=validated_data.get('_id')
                self.logger.info(f"Registro RFC actualizado con ID: {noformato}")
                self.logger.warning("No se actualizara la base de datos")
                status_code = 201 

            if status_code == 201:    

                # Booleanos para   Quien solicita
                if (validated_data.get('region') == "central"):
                    #solicitante = "true"
                    enlacein = "false"
                else:
                    #solicitante = "true"
                    enlacein = "true"
                
                ##IF DE PRUEBA
                enlacein = "true" if validated_data.get ('region') == 'regional' else "false"
                #enlacesolibool = "true" if solicitante == "true" and enlacein == "true" else "false"
                #solicitantebool = "true" if solicitante == "true" and enlacesolibool == "false" else "false"
                #enlaceinbool = "true" if enlacein == "true" and enlacesolibool == "false" else "false"

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

                # Validar si hay temporales
                if (justifica1 != ""): 
                    justEsp1 = "////"
                else:
                    justEsp1 = ""

                if (justifica2 != ""): 
                    justEsp2 = "////"
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

                    file.write("\\newcommand{\\NOTICKET}{"+ validated_data.get('noticket')+"}"+ os.linesep)
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
                tempInter = self.crear_csv_desde_registros(temp_dir, "ALTASINTER.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = validated_data.get('registrosInterBajas', [])   # Obtiene array de los datos
                registros.extend(registrosBajas)                            # Unir registros de bajas y cambios
                self.crear_csv_desde_registros(temp_dir, "BAJASINTER.csv", registros, False) #Se cambia el nombre de la columna

                # Administrador
                # Cambios
                registrosAltas = validated_data.get('registrosAdminCambiosAltas', [])
                registrosBajas = validated_data.get('registrosAdminCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = validated_data.get('registrosAdminAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas)      
                tempAdmin = self.crear_csv_desde_registros(temp_dir, "ALTASADMIN.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = validated_data.get('registrosAdminBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas)   
                self.crear_csv_desde_registros(temp_dir, "BAJASADMIN.csv", registros, False) #Se cambia el nombre de la columna

                # Desarrollador
                # Cambios
                registrosAltas = validated_data.get('registrosDesCambiosAltas', [])
                registrosBajas = validated_data.get('registrosDesCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = validated_data.get('registrosDesAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempDes = self.crear_csv_desde_registros(temp_dir, "ALTASDES.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = validated_data.get('registrosDesBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas) 
                self.crear_csv_desde_registros(temp_dir, "BAJASDES.csv", registros, False) #Se cambia el nombre de la columna

                # Usuario
                # Cambios
                registrosAltas = validated_data.get('registrosUsuaCambiosAltas', [])
                registrosBajas = validated_data.get('registrosUsuaCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = validated_data.get('registrosUsuaAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempUsua = self.crear_csv_desde_registros(temp_dir, "ALTASUSUA.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = validated_data.get('registrosUsuaBajas', [])  # Obtiene array de los datos
                registros.extend(registrosBajas) 
                self.crear_csv_desde_registros(temp_dir, "BAJASUSUA.csv", registros, False) #Se cambia el nombre de la columna

                # Otro
                # Cambios
                registrosAltas = validated_data.get('registrosOtroCambiosAltas', [])
                registrosBajas = validated_data.get('registrosOtroCambiosBajas', [])
                # Añadir que viene de Cambios "C*"
                self.modificar_registros_id(registrosAltas)
                self.modificar_registros_id(registrosBajas)
                # Altas
                registros = validated_data.get('registrosOtroAltas', [])  # Obtiene array de los datos
                registros.extend(registrosAltas) 
                tempOtro = self.crear_csv_desde_registros(temp_dir, "ALTASOTRO.csv", registros, True) #Se cambia el nombre de la columna
                # Bajas
                registros = validated_data.get('registrosOtroBajas', [])  # Obtiene array de los datos
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

                # Compilar latex Aux
                #try:
                 #   subprocess.run(['latex',  "-output-directory",  temp_dir, archivo_tex], check=True)
                  #  self.logger.info(f"Archivo .aux generado para {archivo_tex}")
                #except:
                   
                   # self.logger.error(f"Error generando archivo .aux: {e}")
                    #return jsonify({"error": f"Error al compilar LaTeX Aux: {e}"}), 500

                # Compilar latex PDF
                #try:
                 #   subprocess.run(["pdflatex", "-output-directory", temp_dir, archivo_tex], check=True)
                  #  self.logger.info(f"Archivo PDF generado para {archivo_tex}")
                #except:
                 #   self.logger.error(f"Error generando PDF: {e}")
                  #  return jsonify({"error": f"Error al compilar LaTeX PDF: {e}"}), 500
                
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
                return jsonify(rfc_registro), status_code
            
        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), status_code
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
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
            validated_data = self.forms_schemaInter.load(data)

            # Guardar en BD
            new_inter_data = validated_data
            inter_registro, status_code = self.service.add_internet(new_inter_data)

            if status_code == 201:
                noformato = inter_registro.get('_id')
                self.logger.info(f"Registro INTERNET agregado con ID: {noformato}")
            
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
                return jsonify(inter_registro), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
        finally:
            # Eliminar el directorio temporal
            shutil.rmtree(temp_dir)

    # Actualizar memorandos
    def vpnMemorando(self):
        try: 
            # Recibimos datos
            data = request.get_json()

            # Validamos que existan datos
            if not data:
                return jsonify({"error": "Invalid data"}), 400
            # Validacion
            validated_data = self.actualizarMemo.load(data)

            memorando = validated_data.get('memorando')
            nFormato = validated_data.get('numeroFormato')

            # Llamada al servicio de actualizacion de datos
            DatosVPN, status_code = self.service.actualizar_memorando_vpn(nFormato, memorando)

            if status_code == 201:
                self.logger.info("Informacion actualizada con exito en la base de datos")
                # Agregar o actualizar el campo 'memorando' en DatosVPN
                DatosVPN['memorando'] = memorando
                # Enviar archivo
                return self.vpnmayo(DatosVPN)

            if status_code == 202:
                self.logger.info("No se logro actualizar el memorando")
                return jsonify(DatosVPN), status_code
            if status_code == 400:
                self.logger.error("Ocurrio un error")
                return jsonify(DatosVPN), status_code
            if status_code == 203:
                self.logger.error("No se encontro el Numero de Formato para editar")
                return jsonify(DatosVPN), status_code
            else:
                self.logger.error("Ocurrio otro error aqui")
                return jsonify(DatosVPN), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
    
    def rfcFuncionORol(self):
        try: 
            # Recibimos datos
            data = request.get_json()

            # Validamos que existan datos
            if not data:
                return jsonify({"error": "Invalid data"}), 400
            
            # Validacion
            validated_data = self.actualizarFuncionRol.load(data)

            funcionrol = validated_data.get('funcionrol')
            nFormato = validated_data.get('numeroFormato')

            nRegistro = int(validated_data.get('numeroRegistro'))

            movimiento = validated_data.get('movimientoID')

            # Llamada al servicio de actualizacion de datos
            Datos, status_code = self.service.actualizar_funcionrol_rfc(nFormato, funcionrol, nRegistro, movimiento)

            if status_code == 201:
                self.logger.info("Informacion actualizada con exito en la base de datos")
                # Enviar archivo
                return self.rfc(Datos)
            if status_code == 202:
                self.logger.info("No se logro actualizar el FRO")
                return jsonify(Datos), status_code
            if status_code == 203:
                self.logger.error("No se encontro formato con  el ID especifico")
                return jsonify({"error": "No se encontro el ID de registro"}), status_code
            if status_code == 400:
                self.logger.error("Ocurrio un error")
                return jsonify({"error": "Error nuevo"}), status_code
            else:
                self.logger.error("Ocurrio otro error aqui")
                return jsonify({"error": "Error diferente"}), status_code

        except ValidationError as err:
            self.logger.error(f"Error de validación: {err.messages}")
            return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error generando PDF: {e}")
            return jsonify({"error": "Error generando PDF"}), 500
    
    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200

