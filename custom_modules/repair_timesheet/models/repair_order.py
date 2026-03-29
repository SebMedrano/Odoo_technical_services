from odoo import models, fields, api


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    # One2many giving the repair order access to its timesheet lines.
    # We filter by repair_id so only lines belonging to this repair
    # order appear in the tab — not all analytic lines.
    timesheet_line_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='repair_id',
        string='Timesheets',
    )

    # Computed total hours — sums unit_amount (the hours field on
    # account.analytic.line) across all linked timesheet lines.
    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_total_hours',
        digits=(16, 2),
        store=False,
    )

    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_hours(self):
        # unit_amount is the field name for hours on account.analytic.line.
        # It is named unit_amount because it can represent any unit of
        # measure, not just hours — but in timesheet context it is hours.
        for repair in self:
            repair.total_hours = sum(
                repair.timesheet_line_ids.mapped('unit_amount')
            )

    def write(self, vals):
        result = super().write(vals)
        if 'timesheet_line_ids' in vals:
            self._sync_hours_to_sale_order()
        return result

    def _sync_hours_to_sale_order(self):
        # Finds the labor service line on the linked sale order and
        # updates its quantity to match the total logged hours.
        for repair in self:
            if not repair.sale_order_id:
                continue

            total = sum(repair.timesheet_line_ids.mapped('unit_amount'))

            # Find the labor service line — identified by having a
            # service_client_category set on the product template.
            labor_line = repair.sale_order_id.order_line.filtered(
                lambda l: (
                    l.product_id
                    and l.product_id.product_tmpl_id.service_client_category
                )
            )[:1]

            if labor_line:
                labor_line.sudo().write({'product_uom_qty': total})
