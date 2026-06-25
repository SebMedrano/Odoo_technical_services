import html
from odoo import http
from odoo.http import request

_TEMPLATES = {
    'ees': 'website_lead_forms.contact_form_page_ees',
}
_DEFAULT_TEMPLATE = 'website_lead_forms.contact_form_page'


class WebsiteLeadFormController(http.Controller):

    def _get_form(self, slug):
        return request.env['website.lead.form'].sudo().search(
            [('slug', '=', slug), ('active', '=', True)], limit=1
        )

    def _get_template(self, form):
        return _TEMPLATES.get(form.template, _DEFAULT_TEMPLATE)

    def _validate(self, form, post):
        name = post.get('contact_name', '').strip()
        email = post.get('email_from', '').strip()
        missing = []
        if not name:
            missing.append('Name')
        if not email:
            missing.append('Email')
        if form.template == 'ees':
            if not post.get('subject', '').strip():
                missing.append("Title of your request")
            if not post.get('supervisor_name', '').strip():
                missing.append("Supervisor's name or research group name")
            if not post.get('supervisor_email', '').strip():
                missing.append("Supervisor's email")
        return missing

    def _build_description(self, form, post):
        e = html.escape
        parts = []
        message = post.get('message', '').strip()
        if message:
            parts.append(f'<strong>Message:</strong><br/>{e(message)}')
        if form.template == 'ees':
            for label, key in [
                ("Supervisor / Research Group", 'supervisor_name'),
                ("Supervisor's Email", 'supervisor_email'),
                ("Worktag", 'worktag'),
                ("Speedchart", 'speedchart'),
                ("Department", 'department'),
                ("Priority", 'priority'),
                ("Work Location", 'work_location'),
            ]:
                val = post.get(key, '').strip()
                if val:
                    parts.append(f'<strong>{label}:</strong> {e(val)}')
            repair = post.get('repair_info', '').strip()
            if repair:
                parts.append(f'<strong>Repair Details (Make/Model/Serial):</strong><br/>{e(repair)}')
            delivered = post.get('delivered_to_shop', '').strip()
            if delivered:
                parts.append(f'<strong>Instrument delivered to shop:</strong> {e(delivered)}')
        return '<br/><br/>'.join(parts)

    def _build_confirmation_body(self, form, post):
        e = html.escape
        name = post.get('contact_name', '').strip()
        rows = []

        def row(label, value):
            if value:
                rows.append(
                    f'<tr><td style="padding:6px 12px;font-weight:600;white-space:nowrap;vertical-align:top">'
                    f'{e(label)}</td>'
                    f'<td style="padding:6px 12px;vertical-align:top">{e(value)}</td></tr>'
                )

        row('Name', name)
        row('Email', post.get('email_from', '').strip())

        if form.template == 'ees':
            row('Title of request', post.get('subject', '').strip())
            row("Supervisor / Research Group", post.get('supervisor_name', '').strip())
            row("Supervisor's Email", post.get('supervisor_email', '').strip())
            row('Worktag', post.get('worktag', '').strip())
            row('Speedchart', post.get('speedchart', '').strip())
            row('Department', post.get('department', '').strip())
            row('Priority', post.get('priority', '').strip())
            row('Work Location', post.get('work_location', '').strip())
            row('Repair Details (Make/Model/Serial)', post.get('repair_info', '').strip())
            row('Instrument delivered to shop', post.get('delivered_to_shop', '').strip())
        else:
            row('Phone', post.get('phone', '').strip())
            row('Subject', post.get('subject', '').strip())

        message = post.get('message', '').strip()
        if message:
            rows.append(
                f'<tr><td style="padding:6px 12px;font-weight:600;vertical-align:top">Message</td>'
                f'<td style="padding:6px 12px;vertical-align:top;white-space:pre-wrap">{e(message)}</td></tr>'
            )

        table = (
            '<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px">'
            + ''.join(rows)
            + '</table>'
        )

        return f'''
<div style="font-family:sans-serif;font-size:14px;color:#333;max-width:640px">
    <p>Dear {e(name)},</p>
    <p>
        Thank you for reaching out to {e(form.company_id.name or 'us')}.
        We have received your request and will get back to you shortly.
        Below is a copy of the information you submitted:
    </p>
    <div style="background:#f9f9f9;border:1px solid #e0e0e0;border-radius:4px;padding:8px 0;margin:16px 0">
        {table}
    </div>
    <p>Please do not reply to this email. If you have additional questions, or any information needs to be changed, please contact David Tonkin.</p>
</div>
'''

    def _send_confirmation_email(self, form, post, lead):
        email_to = post.get('email_from', '').strip()
        if not email_to:
            return
        subject_text = post.get('subject', '').strip() or 'your request'
        request.env['mail.mail'].sudo().create({
            'subject': f'We received your request: {subject_text}',
            'email_from': form.company_id.email or request.env.company.email,
            'email_to': email_to,
            'body_html': self._build_confirmation_body(form, post),
            'auto_delete': True,
        }).send()

    @http.route('/contact/<string:form_slug>', type='http', auth='public', website=True)
    def contact_form(self, form_slug, **kwargs):
        form = self._get_form(form_slug)
        if not form:
            return request.not_found()
        return request.render(self._get_template(form), {
            'form': form,
            'post': {},
            'error': None,
        })

    @http.route(
        '/contact/<string:form_slug>/preview',
        type='http', auth='public', website=True, methods=['POST'], csrf=False,
    )
    def contact_form_preview(self, form_slug, **post):
        form = self._get_form(form_slug)
        if not form:
            return request.not_found()

        missing = self._validate(form, post)
        if missing:
            return request.render(self._get_template(form), {
                'form': form,
                'post': post,
                'error': f'The following fields are required: {", ".join(missing)}.',
            })

        return request.render('website_lead_forms.contact_form_preview', {
            'form': form,
            'post': post,
        })

    @http.route(
        '/contact/<string:form_slug>/submit',
        type='http', auth='public', website=True, methods=['POST'], csrf=False,
    )
    def contact_form_submit(self, form_slug, **post):
        form = self._get_form(form_slug)
        if not form:
            return request.not_found()

        missing = self._validate(form, post)
        if missing:
            return request.render(self._get_template(form), {
                'form': form,
                'post': post,
                'error': f'The following fields are required: {", ".join(missing)}.',
            })

        name = post.get('contact_name', '').strip()
        lead_name = post.get('subject', '').strip() or f'New inquiry from {name}' or 'New website inquiry'

        lead = request.env['crm.lead'].sudo().with_context(mail_create_nosubscribe=True).create({
            'name': lead_name,
            'contact_name': name,
            'email_from': post.get('email_from', '').strip(),
            'phone': post.get('phone', '').strip(),
            'description': self._build_description(form, post),
            'user_id': form.user_id.id,
            'team_id': form.team_id.id if form.team_id else False,
            'company_id': form.company_id.id,
            'type': 'opportunity',
        })

        self._send_confirmation_email(form, post, lead)

        return request.render('website_lead_forms.contact_form_success', {'form': form})
