from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_notes = fields.Html(
        string='Opportunity Notes',
        related='opportunity_id.description',
        readonly=True,
        store=False,
    )

    # Service category — mandatory, set at quote stage by supervisor/manager.
    # Visible below the opportunity field on the main page.
    # Propagated to invoice and repair order via related fields.
    service_type = fields.Selection(
        selection=[
            ('repair', 'Repair'),
            ('manufacturing', 'Manufacturing'),
            ('move', 'Move'),
            ('installation', 'Installation'),
            ('maintenance', 'Maintenance'),
        ],
        string='Service Type',
        required=True,
        tracking=True,
        help='Category of work being performed on this order',
    )
