from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    worktag_commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Commercial Partner',
        store=False,
    )

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        domain="[('partner_ids', 'in', [worktag_commercial_partner_id])]",
        tracking=True,
    )

    worktag_name = fields.Char(
        related='worktag_id.name',
        string='Worktag description',
        store=False,
    )

    speedchart_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Speedchart',
        domain="[('partner_ids', 'in', [worktag_commercial_partner_id])]",
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
            if order.worktag_id:
                if order.worktag_id.status == 'inactive':
                    raise UserError(
                        f'Cannot create invoice: worktag "{order.worktag_id.code}" '
                        f'on {order.name} is inactive.'
                    )
                if not order.worktag_id.validated:
                    raise UserError(
                        f'Cannot create invoice: worktag "{order.worktag_id.code}" '
                        f'on {order.name} has not been validated. '
                        f'A manager must check the Validated field on the worktag first.'
                    )

        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)

        for invoice in invoices:
            if not invoice.worktag_id:
                sale_orders = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')
                if sale_orders and sale_orders[0].worktag_id:
                    invoice.worktag_id = sale_orders[0].worktag_id

        return invoices
