from marshmallow import Schema, fields, validate

class ActualizacionFuncionRol(Schema):
    noRegistro=fields.String(required=True)
    funcionRol=fields.String(required=True)
    numeroFormato=fields.String(requiried=True)