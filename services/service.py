from flask import jsonify
from logger.logger import Logger

class Service:
    """Service class to that implements the logic of the CRUD operations for tickets"""

    def __init__(self, db_conn):
        self.logger = Logger()
        self.db_conn = db_conn

    def get_all_VPN(self):
        """Function to fetch all tickets from the database"""
        try:
            vpn = list(self.db_conn.db.vpn.find())
            return vpn
        except Exception as e:
            self.logger.error(f"Error fetching all VPN registers from database: {e}")
            return (
                jsonify({"error": f"Error fetching all VPN registers from database: {e}"}),
                500,
            )

    def add_VPN(self, new_vpn):
        """Function to add a ticket to the database"""

        try:
            # Gets the highest id
            max_id = self.db_conn.db.vpn.find_one(sort=[("_id", -1)])["_id"]
            next_id = max_id + 1
            new_vpn["_id"] = next_id

            self.db_conn.db.vpn.insert_one(new_vpn)
            return new_vpn, 201
        except Exception as e:
            self.logger.error(f"Error adding ticket to database: {e}")
            return jsonify({"error": f"Error adding ticket to database: {e}"}), 500
