from marshmallow import Schema, fields, validate
# from schemas.schemaTablas import TablasSchemaRFC
from schemas.schemaTablasVPN import TablasSchemaSitios
from schemas.schemaTablasVPN import TablasSchemasAcceso

class RegistroSchemaVPNMayo(Schema):
    memorando=fields.String(required=True)
    unidadAdministrativa = fields.String(required=True)
    areaAdscripcion = fields.String(required=True)
    subgerencia = fields.String(required=True)
    nombreEnlace = fields.String(required=True)
    telefonoEnlace = fields.String(required=True)

    solicitante= fields.Boolean(required=True)
    
    nombreInterno=fields.String(required=False)
    puestoInterno= fields.String(required=False)
    correoInterno=fields.String(required=False)
    telefonoInterno=fields.String(required=False)

    nombreExterno=fields.String(required=False)
    correoExterno=fields.String(required=False)
    empresaExterno=fields.String(required=False)
    equipoExterno=fields.String(required=False)

    numeroEmpleadoResponsable=fields.String(required=False)
    nombreResponsable=fields.String(required=False)
    puestoResponsable=fields.String(required=False)
    unidadAdministrativaResponsable=fields.String(required=False)
    telefonoResponsable=fields.String(required=False)

    tipoEquipo=fields.String(required=True)
    sistemaOperativo=fields.String(required=True)
    marca=fields.String(required=True)
    modelo=fields.String(required=True)
    serie=fields.String(required=True)

    nombreAutoriza=fields.String(required=True)
    puestoAutoriza=fields.String(required=True)

    movimiento =fields.String(required=False)
    justificacion=fields.String(required=True)

     # INCISO A)
    registrosSitios = fields.List(fields.Nested(TablasSchemaSitios))
    #INCISIO B)
    registrosAcceso = fields.List(fields.Nested(TablasSchemasAcceso))
