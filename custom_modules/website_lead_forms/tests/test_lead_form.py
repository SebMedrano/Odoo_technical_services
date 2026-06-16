from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestWebsiteLeadFormModel(TransactionCase):
    """Unit tests for the website.lead.form model (no HTTP)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_admin')
        cls.form = cls.env['website.lead.form'].create({
            'name': 'Test Form',
            'slug': 'test-model-slug',
            'user_id': cls.user.id,
            'company_id': cls.env.company.id,
        })

    def test_url_computed_from_slug(self):
        self.assertEqual(self.form.url, '/contact/test-model-slug')

    def test_url_empty_when_slug_not_set(self):
        form = self.env['website.lead.form'].new({'name': 'No Slug Yet'})
        self.assertEqual(form.url, '')

    def test_template_defaults_to_standard(self):
        self.assertEqual(self.form.template, 'standard')

    def test_company_defaults_to_current(self):
        form = self.env['website.lead.form'].create({
            'name': 'Auto Company',
            'slug': 'auto-company-test',
            'user_id': self.user.id,
        })
        self.assertEqual(form.company_id, self.env.company)

    def test_slug_with_spaces_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['website.lead.form'].create({
                'name': 'Bad',
                'slug': 'has spaces',
                'user_id': self.user.id,
                'company_id': self.env.company.id,
            })

    def test_slug_with_uppercase_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['website.lead.form'].create({
                'name': 'Bad',
                'slug': 'HasUpper',
                'user_id': self.user.id,
                'company_id': self.env.company.id,
            })

    def test_slug_with_special_chars_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['website.lead.form'].create({
                'name': 'Bad',
                'slug': 'has@symbol',
                'user_id': self.user.id,
                'company_id': self.env.company.id,
            })

    def test_slug_with_numbers_and_hyphens_accepted(self):
        form = self.env['website.lead.form'].create({
            'name': 'Valid',
            'slug': 'valid-slug-123',
            'user_id': self.user.id,
            'company_id': self.env.company.id,
        })
        self.assertEqual(form.slug, 'valid-slug-123')

    def test_slug_unique_constraint(self):
        with self.assertRaises(Exception):
            self.env['website.lead.form'].create({
                'name': 'Duplicate',
                'slug': 'test-model-slug',
                'user_id': self.user.id,
                'company_id': self.env.company.id,
            })


@tagged('post_install', '-at_install')
class TestWebsiteLeadFormController(HttpCase):
    """Integration tests for the public contact form controller."""

    # Unique email prefix to avoid collisions with real data
    _EMAIL = '@website-lead-forms.test'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = cls.env.ref('base.user_admin')
        company = cls.env.company

        cls.standard_form = cls.env['website.lead.form'].create({
            'name': 'Test Standard Form',
            'slug': 'test-ctrl-standard',
            'user_id': user.id,
            'company_id': company.id,
            'template': 'standard',
        })
        cls.ees_form = cls.env['website.lead.form'].create({
            'name': 'Test EES Form',
            'slug': 'test-ctrl-ees',
            'user_id': user.id,
            'company_id': company.id,
            'template': 'ees',
        })
        cls.inactive_form = cls.env['website.lead.form'].create({
            'name': 'Inactive Form',
            'slug': 'test-ctrl-inactive',
            'user_id': user.id,
            'company_id': company.id,
            'active': False,
        })

    def _leads(self, email):
        self.env['crm.lead'].invalidate_model()
        return self.env['crm.lead'].sudo().search([('email_from', '=', email)])

    # ── GET requests ──────────────────────────────────────────────────────────

    def test_get_standard_form_returns_200(self):
        resp = self.url_open('/contact/test-ctrl-standard')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'test-ctrl-standard/submit', resp.content)

    def test_get_ees_form_returns_ees_template(self):
        resp = self.url_open('/contact/test-ctrl-ees')
        self.assertEqual(resp.status_code, 200)
        # EES template contains supervisor fields absent from standard
        self.assertIn(b'supervisor_name', resp.content)
        self.assertIn(b'supervisor_email', resp.content)

    def test_get_unknown_slug_returns_404(self):
        resp = self.url_open('/contact/this-slug-does-not-exist')
        self.assertEqual(resp.status_code, 404)

    def test_get_inactive_form_returns_404(self):
        resp = self.url_open('/contact/test-ctrl-inactive')
        self.assertEqual(resp.status_code, 404)

    # ── Standard form — valid submissions ─────────────────────────────────────

    def test_standard_valid_submission_shows_success_page(self):
        resp = self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Jane Doe',
            'email_from': 'std-success' + self._EMAIL,
            'subject': 'Hello',
            'message': 'Test message',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Message Sent', resp.content)

    def test_standard_valid_submission_creates_lead(self):
        email = 'std-create-lead' + self._EMAIL
        self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Jane Doe',
            'email_from': email,
            'subject': 'My Request',
            'message': 'Hello world',
        })
        leads = self._leads(email)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads.name, 'My Request')
        self.assertEqual(leads.contact_name, 'Jane Doe')
        self.assertEqual(leads.type, 'opportunity')
        leads.unlink()

    def test_standard_subject_becomes_lead_name(self):
        email = 'std-lead-name' + self._EMAIL
        self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Alice',
            'email_from': email,
            'subject': 'Specific Title',
        })
        lead = self._leads(email)
        self.assertEqual(lead.name, 'Specific Title')
        lead.unlink()

    def test_standard_empty_subject_falls_back_to_contact_name(self):
        email = 'std-fallback' + self._EMAIL
        self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Alice',
            'email_from': email,
            'subject': '',
        })
        lead = self._leads(email)
        self.assertEqual(lead.name, 'New inquiry from Alice')
        lead.unlink()

    def test_standard_lead_routed_to_configured_user(self):
        email = 'std-routing' + self._EMAIL
        self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'Routing Test',
        })
        lead = self._leads(email)
        self.assertEqual(lead.user_id, self.env.ref('base.user_admin'))
        lead.unlink()

    # ── Standard form — validation failures ───────────────────────────────────

    def test_standard_missing_name_bounces(self):
        email = 'std-no-name' + self._EMAIL
        resp = self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': '',
            'email_from': email,
        })
        self.assertIn(b'required', resp.content.lower())
        self.assertFalse(self._leads(email))

    def test_standard_missing_email_bounces(self):
        resp = self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Bob',
            'email_from': '',
        })
        self.assertIn(b'required', resp.content.lower())

    def test_standard_bounced_form_repopulates_fields(self):
        """Fields filled before the error should be pre-filled on the error page."""
        resp = self.url_open('/contact/test-ctrl-standard/submit', data={
            'contact_name': 'Carla',
            'email_from': '',
            'subject': 'Keep This',
        })
        self.assertIn(b'Carla', resp.content)
        self.assertIn(b'Keep This', resp.content)

    # ── EES form — valid submissions ──────────────────────────────────────────

    def test_ees_valid_submission_creates_lead(self):
        email = 'ees-create-lead' + self._EMAIL
        self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob Smith',
            'email_from': email,
            'subject': 'EES Request',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': 'jones@university.test',
        })
        leads = self._leads(email)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads.name, 'EES Request')
        leads.unlink()

    def test_ees_description_contains_supervisor(self):
        email = 'ees-supervisor' + self._EMAIL
        self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'Supervisor Check',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': 'jones@university.test',
        })
        lead = self._leads(email)
        self.assertIn('Dr. Jones', lead.description)
        self.assertIn('jones@university.test', lead.description)
        lead.unlink()

    def test_ees_description_contains_optional_fields(self):
        email = 'ees-optional-fields' + self._EMAIL
        self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'Optional Fields',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': 'jones@university.test',
            'worktag': 'WT-001',
            'speedchart': 'SC-999',
            'department': 'Physics',
            'priority': 'High',
            'repair_info': 'Acme Scope SN-123',
            'message': 'Please fix',
        })
        lead = self._leads(email)
        desc = lead.description
        self.assertIn('WT-001', desc)
        self.assertIn('SC-999', desc)
        self.assertIn('Physics', desc)
        self.assertIn('High', desc)
        self.assertIn('Acme Scope SN-123', desc)
        self.assertIn('Please fix', desc)
        lead.unlink()

    def test_ees_omitted_optional_fields_absent_from_description(self):
        email = 'ees-no-optional' + self._EMAIL
        self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'No Optionals',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': 'jones@university.test',
            'worktag': '',
            'speedchart': '',
        })
        lead = self._leads(email)
        self.assertNotIn('Worktag', lead.description)
        self.assertNotIn('Speedchart', lead.description)
        lead.unlink()

    # ── EES form — validation failures ───────────────────────────────────────

    def test_ees_missing_subject_bounces(self):
        email = 'ees-no-subject' + self._EMAIL
        resp = self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': '',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': 'jones@university.test',
        })
        self.assertIn(b'required', resp.content.lower())
        self.assertFalse(self._leads(email))

    def test_ees_missing_supervisor_name_bounces(self):
        email = 'ees-no-sup-name' + self._EMAIL
        resp = self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'Test',
            'supervisor_name': '',
            'supervisor_email': 'jones@university.test',
        })
        self.assertIn(b'required', resp.content.lower())
        self.assertFalse(self._leads(email))

    def test_ees_missing_supervisor_email_bounces(self):
        email = 'ees-no-sup-email' + self._EMAIL
        resp = self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': email,
            'subject': 'Test',
            'supervisor_name': 'Dr. Jones',
            'supervisor_email': '',
        })
        self.assertIn(b'required', resp.content.lower())
        self.assertFalse(self._leads(email))

    def test_ees_bounced_form_repopulates_fields(self):
        resp = self.url_open('/contact/test-ctrl-ees/submit', data={
            'contact_name': 'Bob',
            'email_from': 'bob@test.test',
            'subject': 'Keep This Title',
            'supervisor_name': '',
            'supervisor_email': '',
        })
        self.assertIn(b'Keep This Title', resp.content)
        self.assertIn(b'Bob', resp.content)
