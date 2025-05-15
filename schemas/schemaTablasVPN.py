from marshmallow import Schema, fields, validate

class TablasSchemaSitios(Schema):
     id=fields.String(required=True)
     movimiento=fields.String(required=True)
     nombreSistema=fields.String(required=True)
     siglas=fields.String(required=True)
     url=fields.String(required=True)
     puertosServicios=fields.String(required=True)
     isNew=fields.String(required=True)
class TablasSchemasAcceso (Schema):
     id =fields.String(required=True)
     movimiento =fields.String(required=True)
     nomenclatura =fields.String(required=False)
     nombreSistema =fields.String(required=False)
     direccion =fields.String(required=True)
     sistemaOperativo =fields.String(required=True)
     isNew=fields.String(required=True)
