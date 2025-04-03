from marshmallow import Schema, fields, validate

class RegistroSchemaVPN(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=64))
    puesto = fields.String(required=True, validate=validate.Length(min=1, max=64))
    ua = fields.String(required=True, validate=validate.Length(min=1, max=64))
    id = fields.String(required=True, validate=validate.Length(min=1, max=32))
    extension = fields.String(required=True, validate=validate.Length(min=1, max=4))
    correo = fields.Email(required=True, validate=validate.Length(min=1, max=64))
    marca = fields.String(required=True, validate=validate.Length(min=1, max=16))
    modelo = fields.String(required=True, validate=validate.Length(min=1, max=16))
    serie = fields.String(required=True, validate=validate.Length(min=1, max=16))
    macadress = fields.String(required=True, validate=validate.Length(min=1, max=18))
    jefe = fields.String(required=True, validate=validate.Length(min=1, max=64))
    puestojefe = fields.String(required=True, validate=validate.Length(min=1, max=64))
    servicios = fields.String(required=True, validate=validate.Length(min=1, max=256))
    justificacion = fields.String(required=True, validate=validate.Length(min=1, max=256))

    movimiento = fields.String(required=True, validate=validate.OneOf(["ALTA", "BAJA", "CAMBIO"]))

    malware = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    vigencia = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    so = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    licencia = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
