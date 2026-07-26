/** @odoo-module */
// Hides the action menu (gear icon) in list and kanban control panels
// for Technician and Supervisor roles. The flag is set server-side in
// models/ir_http.py so the check is synchronous — no Promise needed.

import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(CogMenu.prototype, {
    get hasItems() {
        if (session.techservices_hide_action_menu) {
            return false;
        }
        return super.hasItems;
    },
});
