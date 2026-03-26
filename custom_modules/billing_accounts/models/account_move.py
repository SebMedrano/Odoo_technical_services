from odoo import models, fields


class AccountMove(models.Model):
    # account.move is Odoo's model for both invoices and bills.
    # We extend it to carry the worktag from the sale order.
    _inherit = 'account.move'

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
        help='The billing account (worktag) to be charged for this invoice',
        tracking=True,   # Logs changes in the chatter
        copy=False,      # Do not copy this field when duplicating an invoice
    )

    # Boolean field for the manager to check after the company
    # administrator confirms the worktag via email.
    # This is for tracking only — it does not block payment.
    worktag_confirmed = fields.Boolean(
        string='Worktag Confirmed',
        default=False,
        help='Check this after the company administrator has confirmed '
             'the worktag via email. For tracking purposes only.',
        tracking=True,
        copy=False,
    )
