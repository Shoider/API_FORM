from logger.logger import Logger
from bson.errors import InvalidId

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