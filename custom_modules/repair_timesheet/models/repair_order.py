from odoo import models, fields, api


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    timesheet_line_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='repair_id',
        string='Timesheets',
    )

    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_total_hours',
        digits=(16, 2),
        store=False,
    )

    sale_order_name = fields.Char(
        string='Sale Order Number',
        compute='_compute_sale_order_name',
        store=False,
    )

    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_hours(self):
        for repair in self:
            repair.total_hours = sum(
                repair.timesheet_line_ids.mapped('unit_amount')
            )

    def _compute_sale_order_name(self):
        for repair in self:
            repair.sale_order_name = repair.sale_order_id.name if repair.sale_order_id else ''

    def write(self, vals):
        result = super().write(vals)
        if 'timesheet_line_ids' in vals:
            self._sync_hours_to_sale_order()
        return result

    def _sync_hours_to_sale_order(self):
        for repair in self:
            if not repair.sale_order_id:
                continue
            total = sum(repair.timesheet_line_ids.mapped('unit_amount'))
            labor_line = repair.sale_order_id.order_line.filtered(
                lambda l: (
                    l.product_id
                    and l.product_id.product_tmpl_id.service_client_category
                )
            )[:1]
            if labor_line:
                labor_line.sudo().write({'product_uom_qty': total})
