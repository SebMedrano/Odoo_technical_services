from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_description = fields.Text(string="Product's description")
    x_make = fields.Char(string='Make')
    x_make_part_number = fields.Char(string='Make Part Number')
    x_supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('is_supplier', '=', True)],
        context={'default_is_supplier': True, 'default_is_company': True},
    )
    x_supplier_part_number = fields.Char(string='Supplier Part Number')
    x_alt_supplier_id = fields.Many2one(
        'res.partner',
        string='Alternative Supplier',
        domain=[('is_supplier', '=', True)],
        context={'default_is_supplier': True, 'default_is_company': True},
    )
    x_alt_supplier_part_number = fields.Char(string='Alternative Supplier Part Number')
    x_room_location = fields.Char(string='Room Location')
    x_drawer_location = fields.Char(string='Drawer Location')

    def _flag_suppliers(self, vals):
        for fname in ('x_supplier_id', 'x_alt_supplier_id'):
            partner_id = vals.get(fname)
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                if not partner.is_supplier:
                    partner.write({'is_supplier': True, 'is_company': True})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for vals in vals_list:
            self._flag_suppliers(vals)
        return records

    def write(self, vals):
        result = super().write(vals)
        self._flag_suppliers(vals)
        return result

    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        key = super()._get_view_cache_key(view_id, view_type, **options)
        if view_type == 'form':
            is_manager = self.env.user.has_group('techservices_groups.group_manager')
            is_techservices = self.env.user.has_group('techservices_groups.group_technician')
            key = key + (is_manager, is_techservices)
        return key

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            is_manager = self.env.user.has_group('techservices_groups.group_manager')
            is_techservices = self.env.user.has_group('techservices_groups.group_technician')

            replenish_action = self.env['ir.actions.act_window'].sudo().search(
                [('res_model', '=', 'product.replenish')], limit=1
            )
            if replenish_action and is_techservices and not is_manager:
                for button in arch.xpath(f"//button[@name='{replenish_action.id}']"):
                    button.set('invisible', 'True')

            if is_techservices and not is_manager:
                for page_name in ('sales', 'inventory', 'billing_category'):
                    for node in arch.xpath(f"//page[@name='{page_name}']"):
                        node.set('invisible', 'True')
                for fname in ('type', 'standard_price', 'supplier_taxes_id'):
                    for node in arch.xpath(f"//field[@name='{fname}']"):
                        node.set('invisible', 'True')

        return arch, view
