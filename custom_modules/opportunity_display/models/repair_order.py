from odoo import models, fields


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    # Opportunity linked via the sale order
    opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        related='sale_order_id.opportunity_id',
        readonly=True,
        store=False,
    )

    # Service type from the sale order
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

    # Internal notes from the linked CRM opportunity.
    # Read-only — notes are managed on the opportunity itself.
    opportunity_notes = fields.Html(
        string='Opportunity Notes',
        related='opportunity_id.description',
        readonly=True,
        store=False,
    )
