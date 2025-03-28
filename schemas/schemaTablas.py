from marshmallow import Schema, fields, validate

class TablasSchema(Schema):
    id = fields.Integer(required=True)
    SO = fields.String(required=True)
    FRO = fields.String(allow_none=True)
    IPO = fields.String(allow_none=True)
    SD = fields.String(allow_none=True)
    FRD = fields.String(allow_none=True)
    IPD = fields.String(allow_none=True)
    PRO = fields.String(validate=validate.OneOf(["TCP", "UDP"]), allow_none=True)
    PUER = fields.String(allow_none=True)
    isNew = fields.Boolean(required=True)