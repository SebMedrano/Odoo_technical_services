from odoo import models, fields


class SaleOrder(models.Model):
    # _inherit extends the existing sale.order model.
    # Odoo merges our new field into the existing model —
    # we are not replacing it, just adding to it.
    _inherit = 'sale.order'

    # Many2one links each sale order to one worktag.
    # domain="[('partner_id', '=', partner_id)]" is a dynamic domain —
    # it filters the worktag dropdown to only show worktags that belong
    # to the same company as the one selected on the sale order.
    # This prevents supervisors from accidentally selecting a worktag
    # from a different company.
    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        domain="[('partner_id', '=', partner_id)]",
        help='The billing account (worktag) to be charged for this sale order',
        tracking=True,   # Logs changes to this field in the chatter
    )
