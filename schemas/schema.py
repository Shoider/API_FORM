from marshmallow import Schema, fields, validate

class RegistroSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1))
    puesto = fields.String(required=True, validate=validate.Length(min=1))
    ua = fields.String(required=True, validate=validate.Length(min=1))
    id = fields.String(required=True, validate=validate.Length(min=1))
    extension = fields.String(required=True, validate=validate.Length(min=1))
    correo = fields.Email(required=True)
    marca = fields.String(required=True, validate=validate.Length(min=1))
    modelo = fields.String(required=True, validate=validate.Length(min=1))
    serie = fields.String(required=True, validate=validate.Length(min=1))
    macadress = fields.String(required=True, validate=validate.Length(min=1))
    jefe = fields.String(required=True, validate=validate.Length(min=1))
    puestojefe = fields.String(required=True, validate=validate.Length(min=1))
    servicios = fields.String(required=True, validate=validate.Length(min=1))
    justificacion = fields.String(required=True, validate=validate.Length(min=1))

    movimiento = fields.String(required=True, validate=validate.Length(min=1))
    malware = fields.String(required=True, validate=validate.Length(min=1))
    vigencia = fields.String(required=True, validate=validate.Length(min=1))
    so = fields.String(required=True, validate=validate.Length(min=1))
    licencia = fields.String(required=True, validate=validate.Length(min=1))
