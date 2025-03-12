from marshmallow import Schema, fields, validate

class RegistroSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=256))
    puesto = fields.String(required=True, validate=validate.Length(min=1, max=256))
    ua = fields.String(required=True, validate=validate.Length(min=1, max=256))
    id = fields.String(required=True, validate=validate.Length(min=1, max=256))
    extension = fields.String(required=True, validate=validate.Length(min=1, max=256))
    correo = fields.Email(required=True, validate=validate.Length(min=1, max=256))
    marca = fields.String(required=True, validate=validate.Length(min=1, max=256))
    modelo = fields.String(required=True, validate=validate.Length(min=1, max=256))
    serie = fields.String(required=True, validate=validate.Length(min=1, max=256))
    macadress = fields.String(required=True, validate=validate.Length(min=1, max=256))
    jefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    puestojefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    servicios = fields.String(required=True, validate=validate.Length(min=1, max=256))
    justificacion = fields.String(required=True, validate=validate.Length(min=1, max=256))

    movimiento = fields.String(required=True, validate=validate.Length(min=1, max=256))
    malware = fields.String(required=True, validate=validate.Length(min=1, max=256))
    vigencia = fields.String(required=True, validate=validate.Length(min=1, max=256))
    so = fields.String(required=True, validate=validate.Length(min=1, max=256))
    licencia = fields.String(required=True, validate=validate.Length(min=1, max=256))
