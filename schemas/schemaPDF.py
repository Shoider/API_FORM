from marshmallow import Schema, fields, validate

class CrearPDF(Schema):
    id=fields.String(requiried=True)