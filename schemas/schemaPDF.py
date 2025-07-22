from marshmallow import Schema, fields

class CrearPDF(Schema):
    id=fields.String(required=True)