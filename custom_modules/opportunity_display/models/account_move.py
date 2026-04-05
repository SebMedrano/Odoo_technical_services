from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        related='invoice_line_ids.sale_line_ids.order_id.opportunity_id',
        readonly=True,
        store=False,
    )

    opportunity_notes = fields.Html(
        string='Opportunity Notes',
        related='opportunity_id.description',
        readonly=True,
        store=False,
    )
