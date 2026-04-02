from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # commercial_partner_id is already a native field on sale.order
    # that always resolves to the top-level company, even when a contact
    # is selected as the customer. We expose it here so the view domain
    # on worktag_id can reference it directly.
    # related= reads it from the partner without storing a duplicate.
    worktag_commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Commercial Partner',
        store=False,
    )

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        # Use worktag_commercial_partner_id instead of partner_id
        # so the domain works correctly when a contact is selected.
        domain="[('partner_id', '=', worktag_commercial_partner_id)]",
        help='The billing account (worktag) to be charged for this sale order',
        tracking=True,
    )

    speedchart_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Speedchart',
        domain="[('partner_id', '=', worktag_commercial_partner_id)]",
        help='Select by alternative billing code (speedchart)',
        tracking=True,
        context={'show_speedchart': True},
    )

    @api.onchange('worktag_id')
    def _onchange_worktag_id(self):
        self.speedchart_id = self.worktag_id

    @api.onchange('speedchart_id')
    def _onchange_speedchart_id(self):
        self.worktag_id = self.speedchart_id

    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            if order.worktag_id and order.worktag_id.status == 'inactive':
                raise UserError(
                    f'Cannot create invoice: the worktag "{order.worktag_id.code}" '
                    f'on sale order {order.name} is inactive. '
                    f'Please select an active worktag before creating an invoice.'
                )

        invoices = super()._create_invoices(
            grouped=grouped, final=final, date=date
        )

        for invoice in invoices:
            if not invoice.worktag_id:
                sale_orders = invoice.mapped(
                    'invoice_line_ids.sale_line_ids.order_id'
                )
                if sale_orders:
                    worktag = sale_orders[0].worktag_id
                    if worktag:
                        invoice.worktag_id = worktag

        return invoices
