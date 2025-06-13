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
        if value is None or value == "":
            return  # Campo opcional, permite vacío

        # Si comienza con http o https, es válido
        if value.lower().startswith("http"):
            return

        # Si es una IP válida y comienza con 172.
        try:
            ip = ipaddress.ip_address(value)
            if str(ip).startswith("172."):
                return
        except ValueError:
            pass  # No es una IP, continuar

        raise ValidationError("Debe comenzar con 'http' o ser una IP que inicie con '172.'")
     
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
            ip = ipaddress.ip_address(value)
            if str(ip).startswith("172."):
                return  # Es una IP válida
        except ValueError:
            pass  # No es una IP, continuar con otras validaciones
        # Si ninguna de las anteriores coincide, lanza un error
        raise ValidationError("Debe ser una IP que inicie con '172..")
     
    sistemaOperativo =fields.String(required=False)
    isNew=fields.Boolean(required=False)
