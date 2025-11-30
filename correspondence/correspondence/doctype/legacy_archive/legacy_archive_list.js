frappe.listview_settings['Legacy Archive'] = {
    onload: function (listview) {
        listview.page.add_inner_button(__('Download Import Template'), function () {
            window.open('/assets/correspondence/templates/legacy_archive_template.csv');
        });

        listview.page.add_inner_button(__('Import Data'), function () {
            frappe.set_route('Form', 'Data Import', {
                reference_doctype: 'Legacy Archive',
                import_type: 'Insert New Records'
            });
        });
    }
};
