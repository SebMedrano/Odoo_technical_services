from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('is_supplier', '=', True)],
    )
    x_supplier_part_number = fields.Char(string='Supplier Part Number')
    x_make = fields.Char(string='Make')
