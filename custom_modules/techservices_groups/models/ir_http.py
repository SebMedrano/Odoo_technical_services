from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        user = self.env.user
        # True when the user is a Technician or Supervisor (but not Manager).
        # group_supervisor implies group_technician, so checking group_technician
        # covers both. Checking NOT group_manager excludes Managers.
        is_restricted = (
            user.has_group('techservices_groups.group_technician') and
            not user.has_group('techservices_groups.group_manager')
        )
        result['techservices_messaging_disabled'] = is_restricted
        result['techservices_hide_action_menu'] = is_restricted
        return result
