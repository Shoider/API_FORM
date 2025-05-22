import datetime
from flask import jsonify
from pymongo import ReturnDocument
from logger.logger import Logger
from bson import ObjectId

class Service:
    """Service class to that implements the logic of the CRUD operations for tickets"""

    def __init__(self, db_conn):
        self.logger = Logger()
        self.db_conn = db_conn

    def get_all_VPN(self):
        """Function to fetch all VPN registers from the database"""
        try:
            vpn = list(self.db_conn.db.vpn.find())
            return self._convert_objectid_to_str(vpn)
        except Exception as e:
            self.logger.error(f"Error fetching all VPN registers from database: {e}")
            return (
                jsonify({"error": f"Error fetching all VPN registers from database: {e}"}),
                500,
            )

    def add_VPN(self, new_vpn):
        """Function to add a VPN register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.vpnCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_vpn["_id"] = custom_id

            self.db_conn.db.vpn.insert_one(new_vpn)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding VPN register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding VPN register to database with custom ID: {e}"}), 500
        
    def add_VPNMayo(self, new_vpn):
        """Function to add a VPN Mayo register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.vpnMayoCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_vpn["_id"] = custom_id

            self.db_conn.db.vpnMayo.insert_one(new_vpn)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding VPN Mayo register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding VPN Mayo register to database with custom ID: {e}"}), 500
        
    def add_RFC(self, new_rfc):
        """Function to add a RFC register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.rfcCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_rfc["_id"] = custom_id

            self.db_conn.db.rfc.insert_one(new_rfc)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding RFC register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding RFC register to database with custom ID: {e}"}), 500
        
    def add_tel(self, new_tel):
        """Function to add a TELEFONIA register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.telCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_tel["_id"] = custom_id

            self.db_conn.db.tel.insert_one(new_tel)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding TELEFONIA register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding TELEFONIA register to database with custom ID: {e}"}), 500
        
    def add_internet(self, new_internet):
        """Function to add a INTERNET register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.internetCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_internet["_id"] = custom_id

            self.db_conn.db.internet.insert_one(new_internet)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding INTERNET register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding INTERNET register to database with custom ID: {e}"}), 500
        
    def _convert_objectid_to_str(self, data):
        """Helper function to convert ObjectId to string in a list of dictionaries"""
        if isinstance(data, list):
            for item in data:
                self._convert_objectid_to_str(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
                elif isinstance(value, (list, dict)):
                    self._convert_objectid_to_str(value)
        return data
    

    # Aqui van actualizaciones de memorandos
    def actualizar_memorando_vpn(self, documento_id, nuevo_memorando) -> dict:
        """
        Busca un documento en MongoDB por su ID, actualiza el campo 'memorando'
        y retorna el documento original antes de la actualización.

        Args:
            documento_id (str): El ID del documento a actualizar.
            nuevo_memorando (str): El nuevo valor para el campo 'memorando'.

        Returns:
            dict: El documento original encontrado en la base de datos antes de la actualización,
                o None si no se encuentra el documento.
        """
        try:
            vpn_collection = self.db_conn.db['vpnMayo']
            # Buscar el documento por su ID
            documento_original = vpn_collection.find_one({'_id': documento_id})

            if documento_original:
                # Actualizar el campo 'memorando'
                resultado = vpn_collection.update_one(
                    {'_id': documento_id},
                    {'$set': {'memorando': nuevo_memorando}}
                )

                if resultado.modified_count > 0:
                    return documento_original, 201
                else:
                    # Si no se modificó nada (aunque se encontró el documento),
                    # podría ser un caso a considerar en tu lógica de manejo de errores.
                    return documento_original, 202
            else:
                return None, 203 # No se encontró el documento con el ID proporcionado
            
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            return None, 400
            

    def actualizar_funcionrol_rfc(self, documento_id, nuevo_funcionrol, id_registro, tabla) -> dict:

        try:
            rfc_collection = self.db_conn.db['rfc']
            # Buscar el documento por su ID
            documento_original = rfc_collection.find_one({'_id': documento_id})

            if not documento_original:
                return jsonify({"error": "No se encontró el documento con el ID proporcionado"}), 400

            # Para cambios
            registrosAltas = len(documento_original['registrosInterAltas'])
            registrosBajas = len(documento_original['registrosInterBajas'])

            if (tabla == "ALTAS" and registrosAltas >= id_registro):
                resultado = rfc_collection.update_one(
                    {'_id': documento_id},
                    {'$set': {'registrosInterAltas.$[elem].FRO': nuevo_funcionrol}},
                    array_filters=[{'elem.id': id_registro}]
                )
            elif (tabla == "ALTAS" and registrosAltas < id_registro):
                id_registro = id_registro - registrosAltas
                resultado = rfc_collection.update_one(
                    {'_id': documento_id},
                    {'$set': {'registrosInterCambiosAltas.$[elem].FRO': nuevo_funcionrol}},
                    array_filters=[{'elem.id': id_registro}]
                )
            elif (tabla == "BAJAS" and registrosBajas >= id_registro):
                resultado = rfc_collection.update_one(
                    {'_id': documento_id},
                    {'$set': {'registrosInterBajas.$[elem].FRO': nuevo_funcionrol}},
                    array_filters=[{'elem.id': id_registro}]
                )
            elif (tabla == "BAJAS" and registrosBajas < id_registro):
                id_registro = id_registro - registrosBajas
                resultado = rfc_collection.update_one(
                    {'_id': documento_id},
                    {'$set': {'registrosInterCambiosBajas.$[elem].FRO': nuevo_funcionrol}},
                    array_filters=[{'elem.id': id_registro}]
                )
            else:
                return None, 400
            
            documento_nuevo = rfc_collection.find_one({'_id': documento_id})

            if resultado.modified_count > 0:
                self.logger.info(f"Documento con _id '{documento_id}' actualizado exitosamente.")
                return documento_nuevo, 201
            else:
                self.logger.info(
                    f"No se encontró el subdocumento con id '{id_registro}' "
                    f"en 'registrosInter{tabla}' para el documento con _id '{documento_id}', "
                    f"o el valor de FRO ya era el mismo."
                )
                return documento_nuevo, 202

        except Exception as e:
            self.logger.info(f"Ocurrió un error: {e}")
            return None, 400
