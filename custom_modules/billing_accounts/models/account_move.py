from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    worktag_id = fields.Many2one(
        comodel_name='service.worktag',
        string='Worktag',
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
