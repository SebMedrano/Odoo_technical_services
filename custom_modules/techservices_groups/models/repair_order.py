import ast
from odoo import models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if not self.env.user.has_group('techservices_groups.group_manager'):
            for node in arch.xpath("//page[@name='page_miscellaneous']"):
                node.set('invisible', 'True')
            targets = (
                arch.xpath("//field[@name='move_ids']//field[@name='product_id']")
                + arch.xpath("//field[@name='instrument_id']")
            )
            for node in targets:
                try:
                    opts = ast.literal_eval(node.get('options', '{}'))
                except (ValueError, SyntaxError):
                    opts = {}
                opts['no_quick_create'] = True
                node.set('options', str(opts))
        return arch, view
