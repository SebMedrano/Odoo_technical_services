from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # One2many is the reverse side of the Many2one on service.worktag.
    # It lets us access all worktags belonging to this partner directly
    # from the partner record.
    # 'service.worktag' is the related model.
    # 'partner_id' is the field on that model that points back here.
    worktag_ids = fields.One2many(
        comodel_name='service.worktag',
        inverse_name='partner_id',
        string='Worktags',
        help='All worktags associated with this company',
    )
