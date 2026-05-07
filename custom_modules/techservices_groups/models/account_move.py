from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Server-side guard: mirrors the view-level restriction on the Confirm/Post
        # button.  Prevents a Supervisor from posting an invoice via RPC or any
        # other non-UI pathway (e.g. automated action, API call).
        # Only the Manager role (techservices_groups.group_manager) may post invoices.
        if not self.env.user.has_group('techservices_groups.group_manager'):
            raise UserError(_(
                "Only a Manager can confirm and post invoices. "
                "Please ask a Manager to review and post this invoice."
            ))
        return super().action_post()
