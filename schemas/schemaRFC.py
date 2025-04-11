from marshmallow import Schema, fields, validate

# from schemas.schemaTablas import TablasSchemaRFC
from schemas.schemaTablas import TablasSchemaInter
from schemas.schemaTablas import TablasSchemaAdmin

class RegistroSchemaRFC(Schema):

    # Datos Generales
    tempo = fields.String(required=True, validate=validate.Length(min=1, max=256))
    memo = fields.String(required=True, validate=validate.Length(min=1, max=256))
    descbreve = fields.String(required=True, validate=validate.Length(min=1, max=256))

    nomei = fields.String(required=True, validate=validate.Length(min=1, max=31))
    extei = fields.String(required=True, validate=validate.Length(min=1, max=20))
    puestoei = fields.String(required=True, validate=validate.Length(min=1, max=256))

    noms = fields.String(required=True, validate=validate.Length(min=1, max=31))
    exts = fields.String(required=True, validate=validate.Length(min=1, max=20))
    puestos = fields.String(required=True, validate=validate.Length(min=1, max=256))
    areas = fields.String(required=True, validate=validate.Length(min=1, max=256))
    nombreJefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    puestoJefe = fields.String(required=True, validate=validate.Length(min=1, max=256))
    
    desdet = fields.String(required=True, validate=validate.Length(min=1, max=256))
    desotro = fields.String(required=False, validate=validate.Length(min=0, max=256))
    
    #AQUI NO REQUIERE QUE VALIDE LAS TRES, SOLO DEBE DE TENER ALGUNA 
    justifica = fields.String(required=False)
    justifica2 = fields.String(required=False)
    justifica3 = fields.String(required=False) 

    # Tablas y Tipos de Cambio #

    # Tipos de Cambios
    intersistemas = fields.Boolean(required=False)
    administrador = fields.Boolean(required=False)
    desarrollador = fields.Boolean(required=False)
    usuario = fields.Boolean(required=False)
    otro = fields.Boolean(required=False)

    # Tipo de movimiento
    # InterSistemas
    altaInter = fields.Boolean(required=False)
    bajaInter = fields.Boolean(required=False)
    cambioInter = fields.Boolean(required=False)
    # Administrador
    altaAdmin = fields.Boolean(required=False)
    bajaAdmin = fields.Boolean(required=False)
    cambioAdmin = fields.Boolean(required=False)
    # Desarrollador
    altaDes = fields.Boolean(required=False)
    bajaDes = fields.Boolean(required=False)
    cambioDes = fields.Boolean(required=False)
    # Usuario
    altaUsua = fields.Boolean(required=False)
    bajaUsua = fields.Boolean(required=False)
    cambioUsua = fields.Boolean(required=False)
    # Otro
    altaOtro = fields.Boolean(required=False)
    bajaOtro = fields.Boolean(required=False)
    cambioOtro = fields.Boolean(required=False)

    # Tablas
    # InterSistemas
    registrosInterAltas = fields.List(fields.Nested(TablasSchemaInter))
    registrosInterBajas = fields.List(fields.Nested(TablasSchemaInter))
    registrosInterCambiosAltas = fields.List(fields.Nested(TablasSchemaInter))
    registrosInterCambiosBajas = fields.List(fields.Nested(TablasSchemaInter))
    # Administrador
    registrosAdminAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosAdminBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosAdminCambiosAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosAdminCambiosBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    # Desarrollador
    registrosDesAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosDesBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosDesCambiosAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosDesCambiosBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    # Usuario
    registrosUsuaAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosUsuaBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosUsuaCambiosAltas = fields.List(fields.Nested(TablasSchemaAdmin))
    registrosUsuaCambiosBajas = fields.List(fields.Nested(TablasSchemaAdmin))
    # Otro
    registrosOtroAltas = fields.List(fields.Nested(TablasSchemaInter))
    registrosOtroBajas = fields.List(fields.Nested(TablasSchemaInter))
    registrosOtroCambiosAltas = fields.List(fields.Nested(TablasSchemaInter))
    registrosOtroCambiosBajas = fields.List(fields.Nested(TablasSchemaInter))