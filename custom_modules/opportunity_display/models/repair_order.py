from odoo import models, fields


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    # Related field reading the opportunity from the linked sale order.
    # sale_order_id is the field we confirmed earlier on repair.order
    # in Odoo 18 (line 169 of repair.py).
    # readonly=True — opportunity is managed on the sale order.
    opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        related='sale_order_id.opportunity_id',
        readonly=True,
        store=False,
    )
