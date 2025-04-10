from marshmallow import Schema, fields, validate

class RegistroSchemaInter(Schema):

    fechasoli = fields.String(required=True)
    uaUsuario= fields.String(required=True)
    areaUsuario= fields.String(required=True)
    nombreUsuario= fields.String(required=True)
    puestoUsuario= fields.String(required=True)
    ipUsuario= fields.String(required=True)
    correoUsuario= fields.String(required=True)
    direccion= fields.String(required=True)
    teleUsuario= fields.String(required=True)
    extUsuario= fields.String(required=True)
    nombreJefe= fields.String(required=True)
    puestoJefe= fields.String(required=True)
    
