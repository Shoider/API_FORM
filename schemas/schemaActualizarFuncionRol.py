from marshmallow import Schema, fields, validate

class ActualizacionFuncionRol(Schema):
    numeroFormato=fields.String(required=True)
    funcionrol=fields.String(required=True)
    numeroFormato=fields.String(requiried=True)
    movimiento=fields.String(required=True)