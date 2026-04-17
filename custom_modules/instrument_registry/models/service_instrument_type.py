from odoo import models, fields


class ServiceInstrumentType(models.Model):
    _name = 'service.instrument.type'
    _description = 'Instrument Type'

    name = fields.Char(string='Type', required=True)
