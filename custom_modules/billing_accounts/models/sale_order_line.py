from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


SERVICE_CATEGORIES = {'chemistry', 'ubc', 'external', 'department'}


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Related field that reads the client_category from the sale order's
    # worktag. This makes it accessible in the view domain on product_id
    # so the product dropdown can be filtered dynamically.
    # store=False means it is computed on the fly, not stored in the database.
    worktag_client_category = fields.Selection(
        related='order_id.worktag_id.client_category',
        selection=[
            ('chemistry', 'Chemistry Client'),
            ('ubc', 'UBC Client'),
            ('external', 'External/Private Client'),
            ('department', 'Department Service Client'),
        ],
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

        # Rule 1: Worktag must be selected first
        if not self.order_id.worktag_id:
            self.product_id = False
            return {
                'warning': {
                    'title': 'Worktag Required',
                    'message': (
                        'Please select a Worktag on the sale order before '
                        'adding a labor service product.'
                    ),
                }
            }

        # Rule 2: Product category must match worktag client category
        worktag_category = self.order_id.worktag_id.client_category
        if product_category != worktag_category:
            category_labels = dict(
                self.env['service.worktag']._fields['client_category'].selection
            )
            product_label = category_labels.get(product_category, product_category)
            worktag_label = category_labels.get(worktag_category, worktag_category)
            self.product_id = False
            return {
                'warning': {
                    'title': 'Product Not Allowed for This Worktag',
                    'message': (
                        f'The selected service is for "{product_label}" clients, '
                        f'but the worktag "{self.order_id.worktag_id.code}" '
                        f'belongs to the "{worktag_label}" category.'
                    ),
                }
            }

        # Rule 3: Only one of the 4 service products per sale order
        existing = self.order_id.order_line.filtered(
            lambda l: (
                l != self
                and l.product_id
                and l.product_id.product_tmpl_id.service_client_category
                in SERVICE_CATEGORIES
            )
        )
        if existing:
            self.product_id = False
            return {
                'warning': {
                    'title': 'Only One Labor Service Allowed',
                    'message': (
                        f'This sale order already has a labor service: '
                        f'"{existing[0].product_id.name}". '
                        f'Only one labor service product is allowed per sale order.'
                    ),
                }
            }

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
                    f'Sale order {line.order_id.name}: a labor service product '
                    f'"{line.product_id.name}" requires a worktag to be selected first.'
                )

            worktag_category = line.order_id.worktag_id.client_category
            if product_category != worktag_category:
                category_labels = dict(
                    self.env['service.worktag']._fields['client_category'].selection
                )
                product_label = category_labels.get(product_category, product_category)
                worktag_label = category_labels.get(worktag_category, worktag_category)
                raise ValidationError(
                    f'Product "{line.product_id.name}" is for "{product_label}" clients '
                    f'but worktag "{line.order_id.worktag_id.code}" is "{worktag_label}".'
                )

        for line in self:
            if not line.product_id:
                continue
            if line.product_id.product_tmpl_id.service_client_category not in SERVICE_CATEGORIES:
                continue
            duplicates = line.order_id.order_line.filtered(
                lambda l: (
                    l != line
                    and l.product_id
                    and l.product_id.product_tmpl_id.service_client_category
                    in SERVICE_CATEGORIES
                )
            )
            if duplicates:
                raise ValidationError(
                    f'Sale order {line.order_id.name} already has a labor service. '
                    f'Only one labor service is allowed per sale order.'
                )
