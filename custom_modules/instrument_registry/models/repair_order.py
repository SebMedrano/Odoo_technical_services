from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    instrument_id = fields.Many2one(
        comodel_name='service.instrument',
        string='Instrument',
        tracking=True,
        help='Select an instrument from the registry.',
    )

    # Override product_id to remove the required constraint.
    # In native Odoo, product_id is required on repair orders.
    # We make it optional so instrument-based repairs don't need a product.
    product_id = fields.Many2one(
        required=False,
    )

    @api.constrains('instrument_id', 'product_id')
    def _constrains_instrument_or_product(self):
        # Enforce that at least one of instrument_id or product_id is set.
        # This replaces the native required=True on product_id.
        for repair in self:
            if not repair.instrument_id and not repair.product_id:
                raise ValidationError(
                    'Please select either an Instrument or a Product to repair.'
                )
