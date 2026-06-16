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
            ]:
                val = post.get(key, '').strip()
                if val:
                    parts.append(f'<strong>{label}:</strong> {e(val)}')
            repair = post.get('repair_info', '').strip()
            if repair:
                parts.append(f'<strong>Repair Details (Make/Model/Serial):</strong><br/>{e(repair)}')
        return '<br/><br/>'.join(parts)

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

        request.env['crm.lead'].sudo().create({
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

        return request.render('website_lead_forms.contact_form_success', {'form': form})
