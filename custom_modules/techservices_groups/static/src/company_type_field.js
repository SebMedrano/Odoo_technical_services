/** @odoo-module */
// Registers a custom widget "company_type_no_supplier" that behaves exactly
// like the standard Selection radio widget but hides the 'supplier' option.
// Applied only to the company_type field on the res.partner form via a view
// inherit, so all other Selection fields are unaffected.

import { SelectionField, selectionField } from "@web/views/fields/selection/selection_field";
import { registry } from "@web/core/registry";

class CompanyTypeNoSupplierField extends SelectionField {
    get options() {
        // Keep 'supplier' visible only when the record is already a supplier,
        // so existing supplier records display their type correctly but the
        // option is not available when creating ordinary contacts.
        const current = this.props.record.data[this.props.name];
        return super.options.filter(([value]) => value !== "supplier" || current === "supplier");
    }
}

registry.category("fields").add("company_type_no_supplier", {
    ...selectionField,
    component: CompanyTypeNoSupplierField,
});
