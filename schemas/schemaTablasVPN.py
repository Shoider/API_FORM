from marshmallow import Schema, fields, validate, validates, ValidationError
import ipaddress

class TablasSchemaSitios(Schema):
    id=fields.Integer(required=False)
    movimiento=fields.String(required=False)
    nombreSistema=fields.String(required=False)
    siglas=fields.String(required=False)
    url=fields.String(required=False)

    @validates('url')
    def validate_url_or_ip(self, value):
        if value is None:
            # Si el campo es opcional y no se proporciona, no hay nada que validar
            return
        # Intentar validar como IP
        try:
            ipaddress.ip_address(value)
            return  # Es una IP válida
        except ValueError:
            pass  # No es una IP, continuar con otras validaciones
        # Intentar validar como URL completa (con http/https)
        try:
            validate.URL(schemes=['http', 'https'])(value)
            return # Es una URL completa válida
        except ValidationError:
            pass # No es una URL completa
        # Si ninguna de las anteriores coincide, lanza un error
        raise ValidationError("Debe ser una dirección IP, un nombre de dominio o una URL válida (con http/https).")
     
    puertosServicios=fields.String(required=False)
    isNew=fields.Boolean(required=False)
     
class TablasSchemasAcceso (Schema):
    id =fields.Integer(required=False)
    movimiento =fields.String(required=False)
    nomenclatura =fields.String(required=False, validate=validate.Length(min=7))

    nombreSistema =fields.String(required=False, validate=validate.Length(min=11))
        
    direccion =fields.String(required=False)

    @validates('direccion')
    def validate_url_or_ip(self, value):
        if value is None:
            # Si el campo es opcional y no se proporciona, no hay nada que validar
            return
        # Intentar validar como IP
        try:
            ipaddress.ip_address(value)
            return  # Es una IP válida
        except ValueError:
            pass  # No es una IP, continuar con otras validaciones
        # Si ninguna de las anteriores coincide, lanza un error
        raise ValidationError("Debe ser una dirección IP.")
     
    sistemaOperativo =fields.String(required=False)
    isNew=fields.Boolean(required=False)
