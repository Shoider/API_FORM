from marshmallow import Schema, fields, validate

from marshmallow import Schema, fields, validate

class TablasSchemaRFC(Schema):
    id = fields.Integer(required=True)
    SO = fields.String(required=True, validate=validate.Length(min=1, max=256))
    FRO = fields.String(required=True, validate=validate.Length(min=1, max=256))
    IPO = fields.String(required=True, validate=validate.Length(min=1, max=256))
    SD = fields.String(required=True, validate=validate.Length(min=1, max=256))
    FRD = fields.String(required=True, validate=validate.Length(min=1, max=256))
    IPD = fields.String(required=True, validate=validate.Length(min=1, max=256))
    PRO = fields.String(validate=validate.OneOf(["TCP", "UDP"]), allow_none=True)
    PUER = fields.String(required=True, validate=validate.Length(min=1, max=256))
    isNew = fields.Boolean(required=True)