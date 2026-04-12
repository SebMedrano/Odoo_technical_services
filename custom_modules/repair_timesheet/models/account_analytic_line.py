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

    project_id = fields.Many2one(required=False)

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
