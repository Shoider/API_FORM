from marshmallow import Schema, fields, validate

class ActualizacionMemorando(Schema):
    memorando=fields.String(required=True)
    numeroFormato=fields.String(requiried=True)