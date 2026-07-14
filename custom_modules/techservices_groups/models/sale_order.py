import ast
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_repair_ids = fields.One2many('repair.order', 'sale_order_id', string='Repair Orders')

    x_repair_id = fields.Many2one(
        'repair.order',
        compute='_compute_repair_id',
        string='Linked Repair',
    )
    x_repair_state = fields.Selection(
        [('draft', 'New'), ('confirmed', 'Confirmed'),
         ('under_repair', 'Under Repair'), ('blocked', 'Blocked'),
         ('done', 'Repaired'), ('cancel', 'Cancelled')],
        compute='_compute_repair_fields',
        store=True,
        string='Repair Status',
    )
    x_repair_user_id = fields.Many2one(
        'res.users',
        compute='_compute_repair_fields',
        inverse='_set_repair_user_id',
        store=True,
        string='Repair Responsible',
    )

    @api.depends('x_repair_ids')
    def _compute_repair_id(self):
        for order in self:
            order.x_repair_id = order.x_repair_ids[:1]

    @api.depends('x_repair_ids', 'x_repair_ids.state', 'x_repair_ids.user_id')
    def _compute_repair_fields(self):
        for order in self:
            repair = order.x_repair_ids[:1]
            order.x_repair_state = repair.state if repair else False
            order.x_repair_user_id = repair.user_id if repair else False

    def _set_repair_user_id(self):
        for order in self:
            if order.x_repair_ids:
                order.x_repair_ids[0].user_id = order.x_repair_user_id

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
