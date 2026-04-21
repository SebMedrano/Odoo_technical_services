import ast
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if not self.env.user.has_group('techservices_groups.group_manager'):
            for field_name in ('product_template_id', 'product_id'):
                for node in arch.xpath(
                    f"//field[@name='order_line']//field[@name='{field_name}']"
                ):
                    try:
                        opts = ast.literal_eval(node.get('options', '{}'))
                    except (ValueError, SyntaxError):
                        opts = {}
                    opts['no_quick_create'] = True
                    node.set('options', str(opts))
        return arch, view
