import datetime
from logger.logger import Logger
from bson.errors import InvalidId
from bson import ObjectId

class Service:
    """Service class to that implements the logic of the CRUD operations for tickets"""

    def __init__(self, db_conn):
        self.logger = Logger()
        self.db_conn = db_conn

    def obtener_datos_por_id(self, collection_name: str, document_id: str) -> dict:
        """
        Busca y devuelve un único documento de una colección por su _id.

        Args:
            collection_name (str): El nombre de la colección donde buscar.
            document_id (str): El ID del documento en formato de texto (string).

        Returns:
            dict: El documento encontrado.
            None: Si el documento no se encuentra o el ID es inválido.
        """
        try:
            # Obtener la colección desde la base de datos
            collection = self.db_conn.db[collection_name]
            
            # --- El paso más importante: Convertir el string a ObjectId ---
            datos = collection.find_one({'_id': document_id})
            #object_id_to_find = ObjectId(document_id)
            
            # --- La consulta: Usar find_one para obtener un solo documento ---
            # find_one() es más eficiente que find() si solo esperas un resultado.
            #document = collection.find_one({"_id": object_id_to_find})
            
            # Regresamos el diccionario de datos 
            return datos, 201

        except InvalidId:
            # Esto ocurre si el string del document_id no tiene un formato válido
            # (ej. es muy corto, muy largo o tiene caracteres inválidos).
            print(f"Error: El ID '{document_id}' no es un ObjectId válido.")
            return None, 400
            
        except Exception as e:
            # Manejar otros posibles errores (ej. de conexión)
            print(f"Ocurrió un error inesperado: {e}")
            return None, 500
    
    def borrar_registro(self, noFormato, collection_name):
        
        collection = self.db_conn.db[collection_name]
        resultado = collection.delete_one({'_id': noFormato})

        if resultado:
            return {"mensaje":"registro eliminado con exito"},404
        else:
            return {"mensaje":"id no encontrado"},400
        
    def borrar_contador(self, noFormato, collection_name_counter):
        
        id_documento = noFormato[:6]
        collection = self.db_conn.db[collection_name_counter]
        resultado = collection.update_one({'_id': id_documento}, {'$inc':{'seq':-1}})
        if resultado:
            return {"mensaje":"contador eliminado con exito"},404
        else:
            return {"mensaje":"id no encontrado"},400
    def registrar_error(self,data_collection_name, mensaje):
        """
        Guarda un error en la base de datos 'errores'.

        Args:
            base (str): Nombre de la base de datos relacionada al error.
            mensaje (str): Mensaje descriptivo del error.
            detalles (dict, optional): Detalles adicionales del error.
        """
        now = datetime.datetime.now()
        fecha= now.strftime("%d-%m-%Y %H:%M:%S")
        error_data = {
            "Base de datos": data_collection_name,
            "Mensaje": mensaje,
            "Fecha": fecha
        }
        try:
            # Suponiendo que tienes un cliente MongoDB en self.service.db
            self.db_conn.db["Errores"].insert_one(error_data)
        except Exception as e:
            self.logger.error(f"No se pudo registrar el error.")

    # Ejemplo de uso:
    # self.registrar_error("vpnMayo", "Error al compilar XeLaTeX", {"trace": str(e)})
        
    