from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Related field reading the internal notes from the linked opportunity.
    # Html field type matches the native crm.lead description field type.
    # readonly=True — notes are managed on the opportunity, not the SO.
    # store=False — always read live from the opportunity.
    opportunity_notes = fields.Html(
        string='Opportunity Notes',
        related='opportunity_id.description',
        readonly=True,
        store=False,
    )
