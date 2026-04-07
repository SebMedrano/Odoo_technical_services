from odoo import models, fields


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        related='sale_order_id.opportunity_id',
        readonly=True,
        store=False,
    )

    # Service category read from the linked sale order.
    service_type = fields.Selection(
        related='sale_order_id.service_type',
        selection=[
            ('repair', 'Repair'),
            ('manufacturing', 'Manufacturing'),
            ('move', 'Move'),
            ('installation', 'Installation'),
            ('maintenance', 'Maintenance'),
        ],
        string='Service Type',
        readonly=True,
        store=False,
    )
