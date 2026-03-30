from odoo import models, fields


class ServiceBuilding(models.Model):
    _name = 'service.building'
    _description = 'Building'
    _order = 'name asc'

    name = fields.Char(
        string='Building Name',
        required=True,
    )

    _sql_constraints = [
        (
            'unique_name',
            'UNIQUE(name)',
            'A building with this name already exists.',
        ),
    ]
