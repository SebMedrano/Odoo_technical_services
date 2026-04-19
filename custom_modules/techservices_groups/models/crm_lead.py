from odoo import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_sale_quotations_new(self):
        # Auto-mark opportunity as Won when a Supervisor (non-Manager) creates a quotation
        if (self.env.user.has_group('techservices_groups.group_supervisor')
                and not self.env.user.has_group('techservices_groups.group_manager')):
            self.action_set_won()
        return super().action_sale_quotations_new()
