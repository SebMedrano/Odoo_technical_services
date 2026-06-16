import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WebsiteLeadForm(models.Model):
    _name = 'website.lead.form'
    _description = 'Website Lead Form'
    _order = 'sequence, name'

    name = fields.Char(string='Form Name', required=True)
    sequence = fields.Integer(default=10)
    slug = fields.Char(
        string='URL Slug',
        required=True,
        help='Determines the form URL: /contact/<slug>',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned Salesperson',
        required=True,
    )
    team_id = fields.Many2one('crm.team', string='Sales Team')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    template = fields.Selection([
        ('standard', 'Standard'),
        ('ees', 'EES'),
    ], string='Form Template', default='standard', required=True)
    active = fields.Boolean(default=True)
    url = fields.Char(string='Form URL', compute='_compute_url')

    def _compute_url(self):
        for record in self:
            record.url = f'/contact/{record.slug}' if record.slug else ''

    _sql_constraints = [
        ('slug_unique', 'UNIQUE(slug)', 'URL slug must be unique across all forms.'),
    ]

    @api.constrains('slug')
    def _check_slug_format(self):
        for record in self:
            if not re.match(r'^[a-z0-9-]+$', record.slug):
                raise ValidationError(
                    "Slug may only contain lowercase letters, numbers, and hyphens."
                )
