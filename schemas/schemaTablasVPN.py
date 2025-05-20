from marshmallow import Schema, fields, validate

class TablasSchemaSitios(Schema):
     id=fields.Integer(required=False)
     movimiento=fields.String(required=False)
     nombreSistema=fields.String(required=False)
     siglas=fields.String(required=False)
     url=fields.String(required=False)
     puertosServicios=fields.String(required=False)
     isNew=fields.Boolean(required=False)
     
class TablasSchemasAcceso (Schema):
     id =fields.Integer(required=False)
     movimiento =fields.String(required=False)
     nomenclatura =fields.String(required=False)
     nombreSistema =fields.String(required=False)
     direccion =fields.String(required=False)
     sistemaOperativo =fields.String(required=False)
     isNew=fields.Boolean(required=False)
