from odoo import models, fields, api


class ServiceWorktag(models.Model):
    _name = 'service.worktag'
    _description = 'Service Worktag'
    _rec_name = 'code'

    name = fields.Char(string='Worktag Name', required=True)
    code = fields.Char(string='Worktag Code', required=True)
    cost_centre = fields.Char(string='Cost Centre')
    speedchart = fields.Char(string='Speedchart')

    status = fields.Selection(
        selection=[('active', 'Active'), ('inactive', 'Inactive')],
        string='Status', required=True, default='active',
    )

    client_category = fields.Selection(
        selection=[
            ('chemistry', 'Chemistry Client'),
            ('ubc', 'UBC Client'),
            ('external', 'External/Private Client'),
            ('department', 'Department Service Client'),
        ],
        string='Client Category', required=True,
    )

    validated = fields.Boolean(
        string='Validated',
        default=False,
        help='Must be checked before an invoice can be created. Only managers can change this.',
    )

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='service_worktag_partner_rel',
        column1='worktag_id',
        column2='partner_id',
        string='Companies',
        domain=[('is_company', '=', True), ('is_supplier', '=', False)],
    )

    date_created = fields.Datetime(string='Date Created', related='create_date', store=False)

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'A worktag with this code already exists.'),
        ('unique_speedchart', 'UNIQUE(speedchart)', 'A worktag with this speedchart already exists.'),
    ]

    def _compute_display_name(self):
        for record in self:
            if self.env.context.get('show_speedchart'):
                record.display_name = record.speedchart or record.code
            else:
                record.display_name = record.code

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
        if domain is None:
            domain = []
        if self.env.context.get('show_speedchart') and name:
            domain = [('speedchart', operator, name)] + domain
            return self._search(domain, limit=limit, order=order)
        return super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
