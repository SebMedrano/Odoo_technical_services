from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        domain="[('partner_id', '=', partner_id)]",
        help='Select by primary billing code (worktag code)',
        tracking=True,
    )

    speedchart_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Speedchart',
        domain="[('partner_id', '=', partner_id)]",
        help='Select by alternative billing code (speedchart)',
        tracking=True,
        context={'show_speedchart': True},
    )

    @api.onchange('worktag_id')
    def _onchange_worktag_id(self):
        # Selecting a worktag by code syncs the speedchart field
        # to the same underlying worktag record.
        self.speedchart_id = self.worktag_id

    @api.onchange('speedchart_id')
    def _onchange_speedchart_id(self):
        # Selecting a worktag by speedchart syncs the worktag field
        # to the same underlying worktag record.
        self.worktag_id = self.speedchart_id

    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            if order.worktag_id and order.worktag_id.status == 'inactive':
                raise UserError(
                    f'Cannot create invoice: the worktag "{order.worktag_id.code}" '
                    f'on sale order {order.name} is inactive. '
                    f'Please select an active worktag before creating an invoice.'
                )
        return super()._create_invoices(grouped=grouped, final=final, date=date)
