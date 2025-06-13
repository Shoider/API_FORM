from marshmallow import Schema, fields, validate

class RegistroSchemaTel(Schema):
    
    activacion= fields.String(required=True)
    expiracion= fields.String(required=True)
    nombreUsuario= fields.String(required=True, validate=validate.Length(min=1, max=256))
    correoUsuario= fields.String(required=True, validate=validate.Length(min=1, max=256))
    direccion= fields.String(required=True)
    piso= fields.String(required=False)
    ala= fields.String(required=False)
    uaUsuario= fields.String(required=True)

    nombreEmpleado= fields.String(required=False, validate=validate.Length(min=1, max=32))
    idEmpleado= fields.String(required=False, validate=validate.Length(min=1, max=32))
    extEmpleado= fields.String(required=False, validate=validate.Length(min=1, max=20))
    correoEmpleado= fields.String(required=False, validate=validate.Length(min=1, max=32))
    puestoEmpleado= fields.String(required=False, validate=validate.Length(min=1, max=256))

    justificacion= fields.String(required=True, validate=validate.Length(min=1, max=256))
    puestoUsuario= fields.String(required=True, validate=validate.Length(min=1, max=256))
    nombreJefe= fields.String(required=True, validate=validate.Length(min=1, max=256))
    puestoJefe= fields.String(required=True, validate=validate.Length(min=1, max=256))
    marca= fields.String(required=True)
    modelo= fields.String(required=True, validate=validate.Length(min=1, max=16))
    serie= fields.String(required=True, validate=validate.Length(min=1, max=16))
    version= fields.String(required=True, validate=validate.Length(min=1, max=16))
    movimiento= fields.String(required=True, validate=validate.OneOf(["ALTA", "BAJA", "CAMBIO"]))

    mundo= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    local= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    cLocal= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    nacional= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    cNacional= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    eua= fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    tipoUsuario= fields.String(required=True)

    usuaExterno= fields.Boolean(required=False)
    fecha= fields.String(required=False)
    politicasaceptadas = fields.Boolean(required=True)