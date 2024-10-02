frappe.ui.form.on("Company", "refresh", function(frm) {
    frm.add_custom_button(__("Update delivery date"), () => {
        frappe.confirm(__("This action updates the delivery date of sales orders based on week number >= 2025. Are you sure?"), function() {
            frappe.call({
                method: "ball_customization.ball_customization.uses_cases.update_delivery_date.updt_delivery_date",
                args: {
                    company: frm.doc.name
                },
                freeze: true,
                callback: () => {
                    frappe.msgprint({
                        title: __("Sync Started"),
                        message: __("The process has started in the background."),
                        alert: 1
                    });
                    frappe.set_route("List", "Sales Order",{"company": frm.doc.name});
                }
            });
        });
    });
    frm.add_custom_button(__("Notify delivery date"), () => {
        frappe.confirm(__("This action notifies GP of update of sales orders previously submitted to GP based on week number >= 2025. Are you sure?"), function() {
            frappe.call({
                method: "ball_customization.ball_customization.uses_cases.notify_delivery_date.notify_delivery_date",
                args: {
                    company: frm.doc.name
                },
                freeze: true,
                callback: () => {
                    frappe.msgprint({
                        title: __("Sync Started"),
                        message: __("The process has started in the background."),
                        alert: 1
                    });
                    frappe.set_route("List", "Sales Order",{"company": frm.doc.name});
                }
            });
        });
    });
    });