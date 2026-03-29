from odoo import models, fields, api


class RepairTimesheetLine(models.Model):
    # This is a brand new model — not inherited from account.analytic.line.
    # By not inheriting account.analytic.line we avoid the project/task
    # requirement entirely. This is a simple, focused model that belongs
    # only to repair orders.
    _name = 'repair.timesheet.line'
    _description = 'Repair Timesheet Line'
    _order = 'date asc, id asc'

    # Many2one back to the repair order.
    # ondelete='cascade' means if the repair order is deleted,
    # all its timesheet lines are deleted too — no orphaned records.
    repair_id = fields.Many2one(
        comodel_name='repair.order',
        string='Repair Order',
        required=True,
        ondelete='cascade',
        index=True,
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )

    # Many2one to the employee model from the hr module.
    # The technician filling in the timesheet selects themselves here.
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
    )

    description = fields.Char(
        string='Description',
        required=True,
    )

    # Hours stored as a float.
    # digits=(16, 2) means up to 16 digits total, 2 decimal places.
    # e.g. 1.5 = 1 hour 30 minutes
    hours = fields.Float(
        string='Hours',
        required=True,
        digits=(16, 2),
    )
