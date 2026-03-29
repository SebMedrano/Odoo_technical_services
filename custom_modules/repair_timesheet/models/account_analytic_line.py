from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    # We inherit the native timesheet model instead of creating a new one.
    # This means repair timesheet lines are stored in the same database table
    # as project timesheet lines — making consolidated reports work natively.
    _inherit = 'account.analytic.line'

    # New field linking a timesheet line to a repair order.
    # optional=True in the Many2one means the field is not required —
    # project lines won't have a repair_id and that's fine.
    # ondelete='cascade' means if a repair order is deleted,
    # its timesheet lines are deleted too.
    repair_id = fields.Many2one(
        comodel_name='repair.order',
        string='Repair Order',
        ondelete='cascade',
        index=True,
        help='The repair order this timesheet line belongs to. '
             'Mutually exclusive with Project.',
    )

    # Override project_id to remove the required constraint.
    # In native Odoo, project_id is required on timesheet lines.
    # We make it optional so repair lines don't need a project.
    # required=False overrides the parent field's required=True.
    project_id = fields.Many2one(
        required=False,
    )

    @api.constrains('repair_id', 'project_id')
    def _constrains_repair_or_project(self):
        # Enforce mutual exclusivity — a line belongs to either a repair
        # order OR a project, never both at the same time.
        for line in self:
            if line.repair_id and line.project_id:
                raise ValidationError(
                    'A timesheet line cannot belong to both a repair order '
                    'and a project at the same time. Please choose one.'
                )

    @api.onchange('repair_id')
    def _onchange_repair_id(self):
        # When a repair order is selected, clear the project and task
        # fields to enforce mutual exclusivity in the UI.
        if self.repair_id:
            self.project_id = False
            self.task_id = False

    @api.onchange('project_id')
    def _onchange_project_id_clear_repair(self):
        # When a project is selected, clear the repair order field.
        if self.project_id:
            self.repair_id = False
