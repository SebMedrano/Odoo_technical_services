from odoo import models, fields, api


class ServiceWorktag(models.Model):
    _name = 'service.worktag'
    _description = 'Service Worktag'
    _rec_name = 'code'

    name = fields.Char(
        string='Worktag Name',
        required=True,
        help='Descriptive name for this worktag',
    )

    code = fields.Char(
        string='Worktag Code',
        required=True,
        help='Primary billing code used in the external billing system',
    )

    cost_centre = fields.Char(
        string='Cost Centre',
        help='Alphanumeric cost centre code associated with this worktag',
    )

    speedchart = fields.Char(
        string='Speedchart',
        help='Alternative billing code for this worktag',
    )

    status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        string='Status',
        required=True,
        default='active',
        help='Inactive worktags cannot be used to create invoices',
    )

    # New field: Client Category
    # Selection field with exactly one value required.
    # required=True means the user must pick one before saving.
    client_category = fields.Selection(
        selection=[
            ('chemistry', 'Chemistry Client'),
            ('ubc', 'UBC Client'),
            ('external', 'External/Private Client'),
            ('department', 'Department Service Client'),
        ],
        string='Client Category',
        required=True,
        help='Defines the type of client associated with this worktag',
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Company',
        required=True,
        domain=[('is_company', '=', True)],
        ondelete='restrict',
        help='The company this worktag belongs to',
    )

    _sql_constraints = [
        (
            'unique_code',
            'UNIQUE(code)',
            'A worktag with this code already exists.',
        ),
        (
            'unique_speedchart',
            'UNIQUE(speedchart)',
            'A worktag with this speedchart already exists.',
        ),
    ]

    def _compute_display_name(self):
        for record in self:
            if self.env.context.get('show_speedchart'):
                record.display_name = record.speedchart or record.code
            else:
                record.display_name = record.code

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike',
                     limit=100, order=None):
        if domain is None:
            domain = []
        if self.env.context.get('show_speedchart') and name:
            domain = [('speedchart', operator, name)] + domain
            return self._search(domain, limit=limit, order=order)
        return super()._name_search(
            name=name, domain=domain, operator=operator,
            limit=limit, order=order,
        )
