from odoo import models, fields


class ServiceInstrumentType(models.Model):
    _name = 'service.instrument.type'
    _description = 'Instrument Type'
    _order = 'name asc'

    name = fields.Char(
        string='Type',
        required=True,
    )

    _sql_constraints = [
        (
            'unique_name',
            'UNIQUE(name)',
            'An instrument type with this name already exists.',
        ),
    ]
