from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    # _inherit tells Odoo we are EXTENDING an existing model
    # not creating a new one. Odoo will merge our new field
    # into the existing analytic account model automatically.
    _inherit = 'account.analytic.account'

    external_account_code = fields.Char(
        string='Billing Account Code',
        help='The account identifier used in the external billing system. '
             'This code will appear on the month-end billing report.',
    )
