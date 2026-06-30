import ast
from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    state = fields.Selection(
        selection_add=[('blocked', 'Blocked')],
        ondelete={'blocked': 'set default'},
    )
    x_pre_block_state = fields.Char(copy=False)

    def action_block(self):
        for repair in self:
            repair.x_pre_block_state = repair.state
            repair.state = 'blocked'

    def action_unblock(self):
        for repair in self:
            repair.state = repair.x_pre_block_state or 'under_repair'
            repair.x_pre_block_state = False

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
            for fname in ('repair_line_type', 'quantity', 'picked', 'date', 'date_deadline'):
                for node in arch.xpath(f"//field[@name='move_ids']//field[@name='{fname}']"):
                    node.set('column_invisible', 'True')
        return arch, view
