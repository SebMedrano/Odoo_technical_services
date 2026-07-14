/** @odoo-module */
// Hides "Send message" and "Activities" buttons in the repair.order chatter
// for Technician and Supervisor roles. Uses the session flag set by ir_http.py.

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(Chatter.prototype, {
    get isRepairChatterRestricted() {
        return session.techservices_messaging_disabled === true
            && this.props.threadModel === "repair.order";
    },
});
