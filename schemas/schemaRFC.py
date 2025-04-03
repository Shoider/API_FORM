from marshmallow import Schema, fields, validate

from schemas.schemaTablas import TablasSchema

class RegistroSchemaRFC(Schema):
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

    movimiento = fields.String(required=True, validate=validate.OneOf(["INTER", "ADMIN", "DES", "USUA", "OTRO"]))
    desotro = fields.String(required=False, validate=validate.Length(min=0, max=256))

    # Checar si se puede fields.Boolean()
    ALTA = fields.Boolean(required=True)
    BAJA = fields.Boolean(required=True)
    CAMBIO = fields.Boolean(required=True)

    registrosAltas = fields.List(fields.Nested(TablasSchema))
    registrosCambios = fields.List(fields.Nested(TablasSchema))
    registrosBajas = fields.List(fields.Nested(TablasSchema))
    registros = fields.List(fields.Nested(TablasSchema))