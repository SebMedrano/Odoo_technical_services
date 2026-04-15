from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    repair_id = fields.Many2one(
        comodel_name='repair.order',
        string='Repair Order',
        ondelete='cascade',
        index=True,
        help='The repair order this timesheet line belongs to. '
             'Mutually exclusive with Project.',
    )

    repair_opportunity_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Opportunity',
        compute='_compute_repair_opportunity_id',
        store=False,
    )

    project_id = fields.Many2one(required=False)

    @api.depends('repair_id', 'repair_id.sale_order_id', 'repair_id.sale_order_id.opportunity_id')
    def _compute_repair_opportunity_id(self):
        for line in self:
            if line.repair_id and line.repair_id.sale_order_id:
                line.repair_opportunity_id = line.repair_id.sale_order_id.opportunity_id
            else:
                line.repair_opportunity_id = False

    @api.depends('repair_id', 'repair_id.sale_order_id',
                 'task_id.sale_line_id', 'project_id.sale_line_id',
                 'employee_id', 'project_id.allow_billable')
    def _compute_so_line(self):
        # First run the native computation for project-based lines
        super()._compute_so_line()

        # Then handle repair-based lines that the native method skips
        for timesheet in self.filtered(
            lambda t: t.repair_id
            and not t.is_so_line_edited
            and t._is_not_billed()
        ):
            # Find the labor service line on the repair order's sale order.
            # We identify it by service_client_category — same as our SO sync.
            so = timesheet.repair_id.sale_order_id
            if not so:
                continue

            labor_line = so.order_line.filtered(
                lambda l: (
                    l.product_id
                    and l.product_id.product_tmpl_id.service_client_category
                )
            )[:1]

            if labor_line:
                timesheet.so_line = labor_line

    @api.constrains('repair_id', 'project_id')
    def _constrains_repair_or_project(self):
        for line in self:
            if line.repair_id and line.project_id:
                raise ValidationError(
                    'A timesheet line cannot belong to both a repair order '
                    'and a project at the same time. Please choose one.'
                )

    @api.onchange('repair_id')
    def _onchange_repair_id(self):
        if self.repair_id:
            self.project_id = False
            self.task_id = False

    @api.onchange('project_id')
    def _onchange_project_id_clear_repair(self):
        if self.project_id:
            self.repair_id = False
