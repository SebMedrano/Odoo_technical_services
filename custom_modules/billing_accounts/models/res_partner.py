from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    worktag_ids = fields.Many2many(
        comodel_name='service.worktag',
        relation='service_worktag_partner_rel',
        column1='partner_id',
        column2='worktag_id',
        string='Worktags',
    )

    date_created = fields.Datetime(string='Added on', related='create_date', store=False)
