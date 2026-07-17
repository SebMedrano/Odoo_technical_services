from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

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
        copy=False,
    )

    worktag_confirmed = fields.Boolean(
        string='Worktag Confirmed',
        default=False,
        tracking=True,
        copy=False,
    )

    def _get_invoice_grouping_keys(self):
        return super()._get_invoice_grouping_keys() + ['worktag_id']

    def _post(self, soft=True):
        result = super()._post(soft=soft)
        for move in self:
            if not move.worktag_id and move.move_type == 'out_invoice':
                sale_orders = move.mapped('invoice_line_ids.sale_line_ids.order_id')
                if sale_orders and sale_orders[0].worktag_id:
                    move.worktag_id = sale_orders[0].worktag_id
        return result
