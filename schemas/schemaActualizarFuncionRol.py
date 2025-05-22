from marshmallow import Schema, fields, validate

class ActualizacionFuncionRol(Schema):
    numeroFormato=fields.String(required=True)
    funcionrol=fields.String(required=True)
    numeroRegistro=fields.String(requiried=True)
    movimientoID=fields.String(required=True)