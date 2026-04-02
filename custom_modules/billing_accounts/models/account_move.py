from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Same pattern as sale.order — expose commercial_partner_id
    # so the worktag domain resolves to the company level.
    worktag_commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string='Commercial Partner',
        store=False,
    )

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        domain="[('partner_id', '=', worktag_commercial_partner_id)]",
        help='The billing account (worktag) charged for this invoice',
        tracking=True,
        copy=False,
    )

    worktag_confirmed = fields.Boolean(
        string='Worktag Confirmed',
        default=False,
        help='Check this after the company administrator has confirmed '
             'the worktag via email. For tracking purposes only.',
        tracking=True,
        copy=False,
    )

    def _get_invoice_grouping_keys(self):
        return super()._get_invoice_grouping_keys() + ['worktag_id']

    def _get_source_worktag(self):
        self.ensure_one()
        sale_orders = self.mapped(
            'invoice_line_ids.sale_line_ids.order_id'
        )
        if sale_orders:
            return sale_orders[0].worktag_id
        return False

    def _post(self, soft=True):
        result = super()._post(soft=soft)
        for move in self:
            if not move.worktag_id and move.move_type == 'out_invoice':
                worktag = move._get_source_worktag()
                if worktag:
                    move.worktag_id = worktag
        return result
