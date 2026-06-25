from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('is_supplier', '=', True)],
        context={'default_is_supplier': True, 'default_is_company': True},
    )
    x_supplier_part_number = fields.Char(string='Supplier Part Number')
    x_make = fields.Char(string='Make')
    x_make_part_number = fields.Char(string='Make Part Number')

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            action = self.env.ref('stock.action_product_replenishment', raise_if_not_found=False)
            if action:
                for button in arch.xpath(f"//button[@name='{action.id}']"):
                    button.set('groups', 'techservices_groups.group_manager')
        return arch, view
