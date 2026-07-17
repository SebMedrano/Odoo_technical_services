from odoo import models, fields, api
from odoo.exceptions import ValidationError

SERVICE_CATEGORIES = {'chemistry', 'ubc', 'external', 'department'}


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    worktag_client_category = fields.Selection(
        related='order_id.worktag_id.client_category',
        string='Worktag Client Category',
        store=False,
    )

    @api.onchange('product_id')
    def _onchange_product_id_check_worktag_category(self):
        if not self.product_id:
            return
        product_category = self.product_id.product_tmpl_id.service_client_category
        if not product_category:
            return

        if not self.order_id.worktag_id:
            self.product_id = False
            return {'warning': {'title': 'Worktag Required',
                                'message': 'Please select a Worktag before adding a labor service product.'}}

        worktag_category = self.order_id.worktag_id.client_category
        if product_category != worktag_category:
            category_labels = dict(self.env['service.worktag']._fields['client_category'].selection)
            self.product_id = False
            return {'warning': {'title': 'Product Not Allowed',
                                'message': f'This service is for "{category_labels.get(product_category)}" clients '
                                           f'but the worktag is "{category_labels.get(worktag_category)}".'}}

        existing = self.order_id.order_line.filtered(
            lambda l: l != self and l.product_id
            and l.product_id.product_tmpl_id.service_client_category in SERVICE_CATEGORIES
        )
        if existing:
            self.product_id = False
            return {'warning': {'title': 'Only One Labor Service Allowed',
                                'message': f'This sale order already has "{existing[0].product_id.name}".'}}

    @api.constrains('product_id', 'order_id')
    def _constrains_product_worktag_category(self):
        for line in self:
            if not line.product_id:
                continue
            product_category = line.product_id.product_tmpl_id.service_client_category
            if not product_category:
                continue
            if not line.order_id.worktag_id:
                raise ValidationError(
                    f'Labor service "{line.product_id.name}" requires a worktag on the sale order.')
            worktag_category = line.order_id.worktag_id.client_category
            if product_category != worktag_category:
                category_labels = dict(self.env['service.worktag']._fields['client_category'].selection)
                raise ValidationError(
                    f'Product "{line.product_id.name}" is for '
                    f'"{category_labels.get(product_category)}" but worktag is '
                    f'"{category_labels.get(worktag_category)}".')

        for line in self:
            if not line.product_id:
                continue
            if line.product_id.product_tmpl_id.service_client_category not in SERVICE_CATEGORIES:
                continue
            duplicates = line.order_id.order_line.filtered(
                lambda l: l != line and l.product_id
                and l.product_id.product_tmpl_id.service_client_category in SERVICE_CATEGORIES
            )
            if duplicates:
                raise ValidationError('Only one labor service product is allowed per sale order.')
