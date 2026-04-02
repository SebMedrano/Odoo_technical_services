from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_part_ids = fields.One2many(
        comodel_name='project.task.part',
        inverse_name='task_id',
        string='Parts',
    )

    # Computed total parts cost — useful for display on the task form.
    total_parts_cost = fields.Float(
        string='Total Parts Cost',
        compute='_compute_total_parts_cost',
        digits=(16, 2),
        store=False,
    )

    def _compute_total_parts_cost(self):
        for task in self:
            task.total_parts_cost = sum(
                line.quantity * line.price_unit
                for line in task.task_part_ids
            )
