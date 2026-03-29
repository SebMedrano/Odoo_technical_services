from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # This field tags a product with the client category it belongs to.
    # It is only meaningful for the 4 service products — leave it empty
    # on all other products. When populated, the sale order line
    # validation logic uses it to enforce the category-product rule.
    #
    # The selection values must exactly match those on service.worktag
    # so comparisons work correctly.
    service_client_category = fields.Selection(
        selection=[
            ('chemistry', 'Chemistry Client'),
            ('ubc', 'UBC Client'),
            ('external', 'External/Private Client'),
            ('department', 'Department Service Client'),
        ],
        string='Service Client Category',
        help='If set, this service product can only be added to sale orders '
             'whose worktag has a matching client category. '
             'Leave empty for products that are not one of the 4 labor services.',
    )
