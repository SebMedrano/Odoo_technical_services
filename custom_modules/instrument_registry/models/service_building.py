from odoo import models, fields


class ServiceBuilding(models.Model):
    _name = 'service.building'
    _description = 'Building'

    name = fields.Char(string='Building', required=True)
