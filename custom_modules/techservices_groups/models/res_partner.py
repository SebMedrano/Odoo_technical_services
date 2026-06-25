from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_supplier = fields.Boolean(string='Is Supplier', store=True, default=False)

    x_department_unit = fields.Char(string='Department / Unit')

    @api.onchange('parent_id')
    def _onchange_parent_id_department_unit(self):
        if self.parent_id and self.parent_id.x_department_unit:
            self.x_department_unit = self.parent_id.x_department_unit

    company_type = fields.Selection(
        selection_add=[('supplier', 'Supplier')],
        ondelete={'supplier': lambda recs: recs.write({'is_supplier': False, 'is_company': False})},
    )

    @api.depends('is_company', 'is_supplier')
    def _compute_company_type(self):
        for partner in self:
            if partner.is_supplier:
                partner.company_type = 'supplier'
            elif partner.is_company:
                partner.company_type = 'company'
            else:
                partner.company_type = 'person'

    def _write_company_type(self):
        for partner in self:
            if partner.company_type == 'supplier':
                partner.is_company = True
                partner.is_supplier = True
            elif partner.company_type == 'company':
                partner.is_company = True
                partner.is_supplier = False
            else:
                partner.is_company = False
                partner.is_supplier = False

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'supplier':
            self.is_company = True
            self.is_supplier = True
        elif self.company_type == 'company':
            self.is_company = True
            self.is_supplier = False
        else:
            self.is_company = False
            self.is_supplier = False
