from marshmallow import Schema, fields, validate

class TablasSchemaInter(Schema):
    id = fields.Integer(required=True)
    SO = fields.String(required=False, validate=validate.Length(min=1, max=256))
    FRO = fields.String(required=False, validate=validate.Length(min=1, max=256))
    IPO = fields.String(required=False, validate=validate.Length(min=1, max=256))
    SD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    FRD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    IPD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    PRO = fields.String(validate=validate.OneOf(["TCP", "UDP"]), allow_none=True)
    PUER = fields.String(required=False, validate=validate.Length(min=1, max=256))
    TEMPO = fields.String(validate=validate.OneOf(["TEMPORAL", "PERMANENTE"]), allow_none=True)
    FECHA = fields.String(required=False, validate=validate.Length(min=1, max=256))
    isNew = fields.Boolean(required=True)

class TablasSchemaAdmin(Schema):
    id = fields.Integer(required=True)
    SO = fields.String(required=False, validate=validate.Length(min=1, max=256))
    IPO = fields.String(required=False, validate=validate.Length(min=1, max=256))
    SD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    FRD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    IPD = fields.String(required=False, validate=validate.Length(min=1, max=256))
    PRO = fields.String(validate=validate.OneOf(["TCP", "UDP"]), allow_none=True)
    PUER = fields.String(required=False, validate=validate.Length(min=1, max=256))
    TEMPO = fields.String(validate=validate.OneOf(["TEMPORAL", "PERMANENTE"]), allow_none=True)
    FECHA = fields.String(required=False, validate=validate.Length(min=1, max=256))
    isNew = fields.Boolean(required=False)