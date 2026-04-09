from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_client_category = fields.Selection(
        selection=[
            ('chemistry', 'Chemistry Client'),
            ('ubc', 'UBC Client'),
            ('external', 'External/Private Client'),
            ('department', 'Department Service Client'),
        ],
        string='Service Client Category',
        help='If set, this product can only be added to sale orders whose worktag matches this category.',
    )
