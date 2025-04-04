from marshmallow import Schema, fields, validate

class RegistroSchemaTel(Schema):
    activacion = fields.String(required=True)
    expiracion = fields.String(required=True)
    nombreUsuario = fields.String(required=True)
    curpUsuario = fields.String(required=True)
    direccion = fields.String(required=True)
    uaUsuario = fields.String(required=True)
    nombreEmpleado = fields.String(required=True)
    idEmpleado = fields.String(required=True)
    curpEmpleado = fields.String(required=True)
    extEmpleado = fields.String(required=True)
    correo = fields.Email(required=True)
    puestoEmpleado = fields.String(required=True)
    justificacion = fields.String(required=True)
    puestoUsuario = fields.String(required=True)
    nombreJefe = fields.String(required=True)
    puestoJefe = fields.String(required=True)
    tipoEquipo = fields.String(required=True)
    marca = fields.String(required=True)
    modelo = fields.String(required=True)
    serie = fields.String(required=True)
    version = fields.String(required=True)
    
    movimiento = fields.String(required=True, validate=validate.OneOf(["ALTA", "BAJA", "CAMBIO"]))
    
    tipoUsuario = fields.String(required=True)

    interno = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    mundo = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    local = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    cLocal = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    nacional = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    cNacional = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    eua = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
       