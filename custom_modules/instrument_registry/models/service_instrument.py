from odoo import models, fields, api


class ServiceInstrument(models.Model):
    # Access rights: all internal users can read, write, and create instruments
    # (perm_write=1, perm_create=1 in ir.model.access.csv for base.group_user).
    # Write is required alongside create so that the form view can persist
    # relational field values when saving a new record.
    # Delete (perm_unlink) remains restricted to techservices_groups.group_supervisor.
    _name = 'service.instrument'
    _description = 'Service Instrument'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_names_search = ['make', 'model', 'serial_number', 'partner_id.name']

    name = fields.Char(string='Reference', readonly=True, default='New')
    make = fields.Char(string='Make', required=True, tracking=True)
    model = fields.Char(string='Model', required=True, tracking=True)
    serial_number = fields.Char(string='Serial Number', tracking=True)
    description = fields.Char(string='Description')
    photo = fields.Binary(string='Photo')
    instrument_type_id = fields.Many2one(
        comodel_name='service.instrument.type',
        string='Instrument Type',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        tracking=True,
    )
    building_id = fields.Many2one(
        comodel_name='service.building',
        string='Building',
    )
    room = fields.Char(string='Room')
    notes = fields.Text(string='Notes')
    validated = fields.Boolean(string='Validated', default=False, tracking=True)

    repair_count = fields.Integer(
        string='Repairs',
        compute='_compute_repair_count',
    )

    document_ids = fields.One2many(
        comodel_name='instrument.document',
        inverse_name='instrument_id',
        string='Documents',
    )

    document_count = fields.Integer(
        string='Document Count',
        compute='_compute_document_count',
    )

    def _compute_display_name(self):
        for rec in self:
            parts = [rec.make, rec.model]
            if rec.partner_id:
                parts.append(rec.partner_id.name)
            if rec.description:
                parts.append(rec.description)
            rec.display_name = ' / '.join(filter(None, parts))

    def _compute_repair_count(self):
        for instrument in self:
            instrument.repair_count = self.env['repair.order'].sudo().search_count(
                [('instrument_id', '=', instrument.id)]
            )

    def _compute_document_count(self):
        for instrument in self:
            instrument.document_count = self.env['instrument.document'].search_count(
                [('instrument_id', '=', instrument.id)]
            )

    def action_view_repairs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair Orders',
            'res_model': 'repair.order',
            'view_mode': 'list,form',
            'domain': [('instrument_id', '=', self.id)],
            'context': {'default_instrument_id': self.id},
        }

    def action_open_documents(self):
        self.ensure_one()
        list_view = self.env.ref('instrument_registry.view_instrument_document_list')
        form_view = self.env.ref('instrument_registry.view_instrument_document_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'instrument.document',
            'view_mode': 'list,form',
            'views': [(list_view.id, 'list'), (form_view.id, 'form')],
            'domain': [('instrument_id', '=', self.id)],
            'context': {
                'default_instrument_id': self.id,
                'default_res_model': 'service.instrument',
                'default_res_id': self.id,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('service.instrument') or 'New'
        return super().create(vals_list)
