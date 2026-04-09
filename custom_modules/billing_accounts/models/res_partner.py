from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    worktag_ids = fields.One2many(
        comodel_name='service.worktag',
        inverse_name='partner_id',
        string='Worktags',
    )
