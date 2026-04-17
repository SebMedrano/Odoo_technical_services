from odoo import models, fields


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    instrument_id = fields.Many2one(
        comodel_name='service.instrument',
        string='Instrument',
        tracking=True,
        ondelete='set null',
    )
