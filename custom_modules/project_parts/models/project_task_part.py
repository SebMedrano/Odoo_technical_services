from odoo import models, fields, api
from odoo.exceptions import UserError


class ProjectTaskPart(models.Model):
    _name = 'project.task.part'
    _description = 'Project Task Part'
    _order = 'id asc'

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
        required=True,
        ondelete='cascade',
        index=True,
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=[('type', 'in', ['consu', 'product'])],
        help='Select a part or consumable from inventory',
    )

    description = fields.Char(
        string='Description',
        help='Optional description — defaults to product name if left empty',
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits=(16, 2),
    )

    price_unit = fields.Float(
        string='Unit Price',
        required=True,
        digits=(16, 2),
    )

    # Tracks which sale order line this part created.
    # This is the key field that allows us to update or delete
    # the SO line when the part line changes.
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
        copy=False,
        readonly=True,
        ondelete='set null',
        help='Auto-managed link to the corresponding sale order line',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # Auto-populate price and description from product when selected.
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            if not self.description:
                self.description = self.product_id.name

    def _get_sale_order(self):
        # Helper to find the sale order linked to this part's task.
        # Returns False if no sale order is linked.
        self.ensure_one()
        return self.task_id.project_sale_order_id

    def _sync_to_sale_order(self):
        # Core sync method — called after every create or write.
        # For each part line, either creates or updates the linked SO line.
        for part in self:
            sale_order = part._get_sale_order()

            # No sale order linked to the project — skip silently.
            if not sale_order:
                continue

            # Determine the description to use on the SO line.
            description = part.description or part.product_id.name

            if part.sale_line_id:
                # SO line already exists — update quantity and price.
                part.sale_line_id.sudo().write({
                    'product_uom_qty': part.quantity,
                    'price_unit': part.price_unit,
                    'name': description,
                })
            else:
                # No SO line yet — create one and store the reference.
                # sudo() ensures this works regardless of user's SO access rights.
                so_line = self.env['sale.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'product_id': part.product_id.id,
                    'name': description,
                    'product_uom_qty': part.quantity,
                    'price_unit': part.price_unit,
                    'product_uom': part.product_id.uom_id.id,
                })
                # Write back the SO line ID without triggering another sync.
                part.sudo().write({'sale_line_id': so_line.id})

    @api.model_create_multi
    def create(self, vals_list):
        # Override create to sync to the SO after lines are created.
        records = super().create(vals_list)
        records._sync_to_sale_order()
        return records

    def write(self, vals):
        # Override write to sync to the SO after lines are updated.
        result = super().write(vals)
        self._sync_to_sale_order()
        return result

    def unlink(self):
        # Override unlink to remove the linked SO line when a part is deleted.
        for part in self:
            if part.sale_line_id:
                # Only delete the SO line if the order is still in draft/sent.
                # If the order is confirmed, we zero the quantity instead
                # to avoid breaking the SO.
                if part.sale_line_id.order_id.state in ('draft', 'sent'):
                    part.sale_line_id.sudo().unlink()
                else:
                    part.sale_line_id.sudo().write({'product_uom_qty': 0})
        return super().unlink()
