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
    )

    description = fields.Char(string='Description')

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

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
        copy=False,
        readonly=True,
        ondelete='set null',
    )

    move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock Move',
        copy=False,
        readonly=True,
        ondelete='set null',
        help='Stock move created when this part was consumed',
    )

    move_state = fields.Selection(
        related='move_id.state',
        string='Stock Status',
        readonly=True,
        store=False,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            if not self.description:
                self.description = self.product_id.name

    def _get_sale_order(self):
        self.ensure_one()
        return self.task_id.project_sale_order_id

    def _get_stock_locations(self):
        self.ensure_one()
        company = self.task_id.project_id.company_id
        if not company:
            company = self.env.company

        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', company.id)], limit=1
        )
        if not warehouse:
            raise UserError(
                f'No warehouse found for company "{company.name}". '
                f'Please configure a warehouse before consuming parts.'
            )

        source_location = warehouse.lot_stock_id

        dest_location = self.env['stock.location'].search(
            [('usage', '=', 'production'), ('company_id', 'in', [company.id, False])],
            limit=1
        )
        if not dest_location:
            raise UserError(
                f'No production location found for company "{company.name}". '
                f'Please check your stock locations configuration.'
            )

        return source_location, dest_location

    def _create_stock_move(self, qty=None):
        # Creates and immediately validates a stock move.
        # Uses immediate_transfer=True context to force validation
        # without requiring prior stock reservation — this avoids
        # leaving pending transfers in the inventory that need
        # manual validation.
        self.ensure_one()
        source_location, dest_location = self._get_stock_locations()
        company = self.task_id.project_id.company_id or self.env.company
        move_qty = qty or self.quantity

        move = self.env['stock.move'].sudo().create({
            'name': f'{self.task_id.name} - {self.product_id.name}',
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': move_qty,
            'quantity': move_qty,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'company_id': company.id,
            'origin': self.task_id.name,
        })

        move._action_confirm()
        # immediate_transfer=True forces _action_done to complete
        # the move without requiring full reservation first.
        # This is equivalent to clicking "Validate" on an immediate
        # transfer dialog in the Odoo UI.
        move.with_context(immediate_transfer=True).sudo()._action_done()

        return move

    def _reverse_stock_move(self, qty=None):
        self.ensure_one()
        if not self.move_id:
            return

        qty_to_reverse = qty or self.quantity
        source_location, dest_location = self._get_stock_locations()
        company = self.task_id.project_id.company_id or self.env.company

        reverse_move = self.env['stock.move'].sudo().create({
            'name': f'Reversal: {self.task_id.name} - {self.product_id.name}',
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': qty_to_reverse,
            'quantity': qty_to_reverse,
            'location_id': dest_location.id,
            'location_dest_id': source_location.id,
            'company_id': company.id,
            'origin': f'Reversal: {self.task_id.name}',
        })

        reverse_move._action_confirm()
        reverse_move.with_context(immediate_transfer=True).sudo()._action_done()

    def _sync_to_sale_order(self):
        for part in self:
            sale_order = part._get_sale_order()
            if not sale_order:
                continue
            description = part.description or part.product_id.name
            if part.sale_line_id:
                part.sale_line_id.sudo().write({
                    'product_uom_qty': part.quantity,
                    'price_unit': part.price_unit,
                    'name': description,
                })
            else:
                so_line = self.env['sale.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'product_id': part.product_id.id,
                    'name': description,
                    'product_uom_qty': part.quantity,
                    'price_unit': part.price_unit,
                    'product_uom': part.product_id.uom_id.id,
                })
                part.sudo().write({'sale_line_id': so_line.id})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for part in records:
            move = part._create_stock_move()
            part.sudo().write({'move_id': move.id})
            part._sync_to_sale_order()
        return records

    def write(self, vals):
        if 'quantity' in vals:
            for part in self:
                old_qty = part.quantity
                new_qty = vals['quantity']
                result = super(ProjectTaskPart, part).write(vals)
                if part.move_id and new_qty != old_qty:
                    diff = new_qty - old_qty
                    if diff > 0:
                        part._create_stock_move(qty=diff)
                    else:
                        part._reverse_stock_move(qty=abs(diff))
                part._sync_to_sale_order()
            return True
        else:
            result = super().write(vals)
            self._sync_to_sale_order()
            return result

    def unlink(self):
        for part in self:
            if part.move_id and part.move_id.state == 'done':
                part._reverse_stock_move()
            if part.sale_line_id:
                if part.sale_line_id.order_id.state in ('draft', 'sent'):
                    part.sale_line_id.sudo().unlink()
                else:
                    part.sale_line_id.sudo().write({'product_uom_qty': 0})
        return super().unlink()
