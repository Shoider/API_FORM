from marshmallow import Schema, fields, validate

class RegistroSchema2(Schema):
    tempo = fields.String(required=True, validate=validate.Length(min=1, max=256))
    memo = fields.String(required=True, validate=validate.Length(min=1, max=256))
    descbreve = fields.String(required=True, validate=validate.Length(min=1, max=256))

    nomei = fields.String(required=True, validate=validate.Length(min=1, max=31))
    extei = fields.String(required=True, validate=validate.Length(min=1, max=4))
    puestoei = fields.String(required=True, validate=validate.Length(min=1, max=256))

    noms = fields.String(required=True, validate=validate.Length(min=1, max=31))
    exts = fields.String(required=True, validate=validate.Length(min=1, max=4))
    puestos = fields.String(required=True, validate=validate.Length(min=1, max=256))
    areas = fields.String(required=True, validate=validate.Length(min=1, max=256))
    nombreJefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    puestoJefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    
    desdet = fields.String(required=True, validate=validate.Length(min=1, max=256))

    # No entendi    D:
    #AQUI NO REQUIERE QUE VALIDE LAS TRES, SOLO DEBE DE TENER ALGUNA 
    justifica = fields.String(required=True, validate=validate.Length(min=1, max=256))
    justifica2 = fields.String(required=True, validate=validate.Length(min=1, max=256))
    justifica3 = fields.String(required=True, validate=validate.Length(min=1, max=256)) 

   # VALIDACIONES DE TIPO PENDIENTES
    INTER = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    ADMIN = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    DES = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    USUA = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))
    OTRO = fields.String(required=True, validate=validate.OneOf(["SI", "NO"]))

    movimiento = fields.String(required=True, validate=validate.OneOf(["INTER", "ADMIN", "DES", "USUA", "OTRO"]))
    desotro = fields.String(required=False, validate=validate.Length(min=1, max=32))

    # Checar si se puede fields.Boolean()
    ALTA = fields.Boolean(required=True, validate=validate.OneOf(["true", "false"]))
    BAJA = fields.Boolean(required=True, validate=validate.OneOf(["true", "false"]))
    CAMBIO = fields.Boolean(required=True, validate=validate.OneOf(["true", "false"]))


    #validadores para los csv de ALTAS, BAJAS, CAMBIOS 