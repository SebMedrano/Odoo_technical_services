import io
import base64
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class WorktagBillingReportWizard(models.TransientModel):
    _name = 'worktag.billing.report.wizard'
    _description = 'Worktag Billing Report'

    date_from = fields.Date(
        string='From',
        required=True,
        default=lambda self: date.today().replace(day=1),
    )

    date_to = fields.Date(
        string='To',
        required=True,
        default=fields.Date.today,
    )

    report_file = fields.Binary(string='Report File', readonly=True)
    report_filename = fields.Char(string='Filename', readonly=True)

    def action_generate_report(self):
        if self.date_from > self.date_to:
            raise UserError('The start date must be before the end date.')

        if not xlsxwriter:
            raise UserError(
                'The xlsxwriter library is required. '
                'Please contact your administrator to install it.'
            )

        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('payment_state', '=', 'paid'),
            ('worktag_id', '!=', False),
        ])

        if not invoices:
            raise UserError(
                f'No paid invoices with worktags found between '
                f'{self.date_from} and {self.date_to}.'
            )

        worktag_data = {}
        for invoice in invoices:
            worktag = invoice.worktag_id
            wid = worktag.id
            if wid not in worktag_data:
                worktag_data[wid] = {
                    'code': worktag.code or '',
                    'speedchart': worktag.speedchart or '',
                    'company': worktag.partner_id.name or '',
                    'cost_centre': worktag.cost_centre or '',
                    'amount': 0.0,
                }
            worktag_data[wid]['amount'] += invoice.amount_total

        rows = sorted(
            worktag_data.values(),
            key=lambda r: (r['company'], r['code'])
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Worktag Billing Report')

        title_fmt = workbook.add_format({'bold': True, 'font_size': 14})
        subtitle_fmt = workbook.add_format({'italic': True, 'font_size': 10, 'font_color': '#666666'})
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
        })
        cell_fmt = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        amount_fmt = workbook.add_format({
            'border': 1, 'valign': 'vcenter',
            'num_format': '#,##0.00', 'align': 'right',
        })
        total_label_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'bg_color': '#ECF0F1',
        })
        total_amount_fmt = workbook.add_format({
            'bold': True, 'border': 1, 'bg_color': '#ECF0F1',
            'num_format': '#,##0.00', 'align': 'right',
        })

        worksheet.merge_range('A1:E1', 'Worktag Billing Report', title_fmt)
        worksheet.write('A2',
            f'Period: {self.date_from.strftime("%B %d, %Y")} — {self.date_to.strftime("%B %d, %Y")}',
            subtitle_fmt)
        worksheet.write('A3', f'Generated: {date.today().strftime("%B %d, %Y")}', subtitle_fmt)

        headers = ['Worktag Code', 'Speedchart', 'Company', 'Cost Centre', 'Amount']
        col_widths = [18, 15, 30, 15, 15]
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            worksheet.write(4, col, header, header_fmt)
            worksheet.set_column(col, col, width)
        worksheet.set_row(4, 20)

        grand_total = 0.0
        for row_idx, row in enumerate(rows, start=5):
            worksheet.write(row_idx, 0, row['code'], cell_fmt)
            worksheet.write(row_idx, 1, row['speedchart'], cell_fmt)
            worksheet.write(row_idx, 2, row['company'], cell_fmt)
            worksheet.write(row_idx, 3, row['cost_centre'], cell_fmt)
            worksheet.write(row_idx, 4, row['amount'], amount_fmt)
            grand_total += row['amount']

        total_row = len(rows) + 5
        worksheet.write(total_row, 0, '', total_label_fmt)
        worksheet.write(total_row, 1, '', total_label_fmt)
        worksheet.write(total_row, 2, '', total_label_fmt)
        worksheet.write(total_row, 3, 'TOTAL', total_label_fmt)
        worksheet.write(total_row, 4, grand_total, total_amount_fmt)
        worksheet.freeze_panes(5, 0)

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        filename = (
            f'worktag_billing_report_'
            f'{self.date_from.strftime("%Y%m%d")}_'
            f'{self.date_to.strftime("%Y%m%d")}.xlsx'
        )

        self.write({'report_file': file_data, 'report_filename': filename})

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
