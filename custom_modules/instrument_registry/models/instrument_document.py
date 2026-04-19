from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InstrumentDocument(models.Model):
    _name = 'instrument.document'
    _description = 'Instrument Document'
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _order = 'sequence, name'

    ir_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Related Attachment',
        required=True,
        ondelete='cascade',
    )

    instrument_id = fields.Many2one(
        comodel_name='service.instrument',
        string='Instrument',
        required=True,
        ondelete='cascade',
        index=True,
    )

    description = fields.Char(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    @api.onchange('url')
    def _onchange_url(self):
        for doc in self:
            if doc.type == 'url' and doc.url and \
                    not doc.url.startswith(('https://', 'http://', 'ftp://')):
                raise ValidationError(
                    'Please enter a valid URL.\n'
                    'Example: https://www.example.com\n\n'
                    f'Invalid URL: {doc.url}'
                )

    @api.model_create_multi
    def create(self, vals_list):
        # Set res_model and res_id on the underlying ir.attachment
        # so files are properly linked to the instrument record.
        for vals in vals_list:
            if 'instrument_id' in vals:
                vals.setdefault('res_model', 'service.instrument')
                vals.setdefault('res_id', vals['instrument_id'])
        return super().create(vals_list)

    def unlink(self):
        attachments = self.ir_attachment_id
        res = super().unlink()
        return res and attachments.unlink()
