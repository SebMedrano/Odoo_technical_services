/** @odoo-module */
// Hides the top-bar messaging panel (chat + channel menu) for Technician and
// Supervisor roles.  The flag is set server-side in models/ir_http.py so the
// check is synchronous here — no Promise needed.

import { MessagingMenu } from "@mail/core/public_web/messaging_menu";  // ensure this runs after messaging_menu.js
import { registry } from "@web/core/registry";
import { session } from "@web/session";

if (session.techservices_messaging_disabled) {
    registry.category("systray").remove("mail.messaging_menu");
}

// Re-export so the import above is not optimised away as a side-effect-free
// import by the bundler.
export { MessagingMenu };
