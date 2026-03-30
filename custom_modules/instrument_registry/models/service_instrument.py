from odoo import models, fields, api


class ServiceInstrument(models.Model):
    _name = 'service.instrument'
    _description = 'Instrument'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    # --- Auto-generated reference ---
    reference = fields.Char(
        string='Instrument ID',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'service.instrument'
        ),
    )

    # --- Identification ---
    photo = fields.Binary(
        string='Photo',
        attachment=True,
    )

    make = fields.Char(
        string='Make',
        required=True,
        tracking=True,
    )

    model = fields.Char(
        string='Model',
        required=True,
        tracking=True,
    )

    serial_number = fields.Char(
        string='Serial Number',
        tracking=True,
    )

    # New field: description of the instrument
    description = fields.Char(
        string='Description',
        tracking=True,
        help='Brief description of the instrument',
    )

    # Display name: "Make / Model / Customer / Description"
    # Serial number removed per updated requirement.
    display_name = fields.Char(
        string='Name',
        compute='_compute_display_name',
        store=True,
    )

    @api.depends('make', 'model', 'partner_id', 'description')
    def _compute_display_name(self):
        for instrument in self:
            parts = [instrument.make, instrument.model]
            if instrument.partner_id:
                parts.append(instrument.partner_id.name)
            if instrument.description:
                parts.append(instrument.description)
            instrument.display_name = ' / '.join(filter(None, parts))

    instrument_type_id = fields.Many2one(
        comodel_name='service.instrument.type',
        string='Type',
        tracking=True,
    )

    # --- Ownership ---
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        tracking=True,
        help='The customer or organization that owns this instrument',
    )

    # --- Location ---
    building_id = fields.Many2one(
        comodel_name='service.building',
        string='Building',
        tracking=True,
    )

    room = fields.Char(
        string='Room',
        tracking=True,
    )

    # --- Notes ---
    notes = fields.Text(
        string='Internal Notes',
    )

    # --- Smart button counts ---
    repair_count = fields.Integer(
        string='Repairs',
        compute='_compute_repair_count',
    )

    sale_count = fields.Integer(
        string='Sale Orders',
        compute='_compute_sale_count',
    )

    @api.depends()
    def _compute_repair_count(self):
        for instrument in self:
            instrument.repair_count = self.env['repair.order'].search_count([
                ('instrument_id', '=', instrument.id)
            ])

    @api.depends()
    def _compute_sale_count(self):
        for instrument in self:
            repairs = self.env['repair.order'].search([
                ('instrument_id', '=', instrument.id),
                ('sale_order_id', '!=', False),
            ])
            sale_ids = repairs.mapped('sale_order_id').ids
            instrument.sale_count = len(set(sale_ids))

    def action_view_repairs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair Orders',
            'res_model': 'repair.order',
            'view_mode': 'list,form',
            'domain': [('instrument_id', '=', self.id)],
            'context': {'default_instrument_id': self.id},
        }

    def action_view_sales(self):
        repairs = self.env['repair.order'].search([
            ('instrument_id', '=', self.id),
            ('sale_order_id', '!=', False),
        ])
        sale_ids = repairs.mapped('sale_order_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', sale_ids)],
        }
