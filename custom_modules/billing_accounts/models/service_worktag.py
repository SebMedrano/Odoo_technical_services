from odoo import models, fields


class ServiceWorktag(models.Model):
    # _name defines a brand new model in Odoo's database.
    # Odoo will create a table called 'service_worktag' for this.
    # We use _name (not _inherit) because this is a new concept,
    # not an extension of something that already exists.
    _name = 'service.worktag'

    # _description is a human-readable label for the model.
    # Odoo requires this — you will get a warning without it.
    _description = 'Service Worktag'

    # _rec_name tells Odoo which field to use when displaying
    # a worktag as a label elsewhere (e.g. in a dropdown).
    # We use 'code' so dropdowns show "ACME-IT-001" not "IT Budget".
    _rec_name = 'code'

    # Char is a simple text field (varchar in the database).
    # required=True means Odoo will not save the record without it.
    name = fields.Char(
        string='Worktag Name',
        required=True,
        help='Descriptive name for this worktag, e.g. IT Infrastructure Budget 2026',
    )

    code = fields.Char(
        string='Worktag Code',
        required=True,
        help='The identifier used in the external billing system, e.g. ACME-IT-001',
    )

    # Many2one creates a foreign key relationship.
    # This links each worktag to exactly one company (res.partner).
    # 'res.partner' is Odoo's built-in model for contacts and companies.
    # domain=[('is_company', '=', True)] filters the dropdown to show
    # only companies, not individual contacts.
    # ondelete='restrict' means Odoo will refuse to delete a company
    # if it still has worktags attached — prevents orphaned records.
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Company',
        required=True,
        domain=[('is_company', '=', True)],
        ondelete='restrict',
        help='The company this worktag belongs to',
    )

    # Boolean adds a True/False field.
    # active=True is a special Odoo convention — when active=False
    # the record is archived and hidden from normal views and dropdowns
    # without being permanently deleted.
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this worktag without deleting it',
    )

    # _sql_constraints enforces uniqueness at the database level,
    # not just in Python. This is more reliable than a Python check
    # because it prevents duplicates even under concurrent requests.
    # The format is: [('constraint_name', 'sql_rule', 'error_message')]
    _sql_constraints = [
        (
            'unique_code',
            'UNIQUE(code)',
            'A worktag with this code already exists. Each worktag code must be unique.'
        ),
    ]
