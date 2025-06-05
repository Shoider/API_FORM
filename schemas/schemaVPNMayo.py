from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from schemas.schemaTablasVPN import TablasSchemaSitios
from schemas.schemaTablasVPN import TablasSchemasAcceso

class RegistroSchemaVPNMayo(Schema):
    memorando=fields.String(required=False)
    numeroFormato=fields.String(requiried=False)
    _id=fields.String(requiried=False)
    
    unidadAdministrativa = fields.String(required=True)
    areaAdscripcion = fields.String(required=True)
    subgerencia = fields.String(required=True)
    nombreEnlace = fields.String(required=True)
    telefonoEnlace = fields.String(required=True, validate=validate.Length(min=8, max=20))
    
    nombreInterno=fields.String(required=False)
    puestoInterno= fields.String(required=False)
    correoInterno=fields.String(required=False)
    telefonoInterno=fields.String(required=False)

    @validates('telefonoInterno')
    def validate_telefonoInterno(self, value):
        if value is None:
            return
        if len(value) < 8:
           raise ValidationError ("Debe de ser un teléfono de 8 caracteres mínimo")

    nombreExterno=fields.String(required=False)
    correoExterno=fields.String(required=False)
    empresaExterno=fields.String(required=False)
    equipoExterno=fields.String(required=False)

    numeroEmpleadoResponsable=fields.String(required=False)
    nombreResponsable=fields.String(required=False)
    puestoResponsable=fields.String(required=False)
    unidadAdministrativaResponsable=fields.String(required=False)
    telefonoResponsable=fields.String(required=False)

    #@validates('telefonoResponsable')
    #def validate_telefonoResponsable(self, value):
    #    if value is None:
    #        return
    #    if len(value) < 8:
    #       raise ValidationError ("Debe de ser un teléfono de 8 caracteres mínimo")

    
    tipoEquipo=fields.String(required=True)
    sistemaOperativo=fields.String(required=True)
    marca=fields.String(required=True)
    modelo=fields.String(required=True)
    serie=fields.String(required=True)

    nombreAutoriza=fields.String(required=True)
    puestoAutoriza=fields.String(required=True)

    movimiento =fields.String(required=False)
    justificacion=fields.String(required=True, validate=validate.Length(min=50, max=256))

    # Booleanos
    solicitante = fields.String(required=True)
    cuentaUsuario = fields.Boolean(required=True)
    accesoWeb = fields.Boolean(required=True)
    accesoRemoto = fields.Boolean(required=True)

    politicasaceptadas = fields.Boolean(required=True)

    # INCISO B)
    registrosWeb = fields.List(fields.Nested(TablasSchemaSitios))
    # INCISO C)
    registrosRemoto = fields.List(fields.Nested(TablasSchemasAcceso))  
