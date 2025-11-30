// Client Script for Incoming Letter
// Enhances UI with auto-fill, related documents panel, and OCR processing

frappe.ui.form.on('Incoming Letter', {
    refresh: function (frm) {
        // Add custom buttons
        add_custom_buttons(frm);

        // Show related documents panel
        if (!frm.is_new()) {
            show_related_documents_panel(frm);
        }

        // Show version history
        if (!frm.is_new()) {
            show_version_history_button(frm);
        }

        // Disable editing if archived
        if (frm.doc.is_archived && !frappe.user.has_role('System Manager')) {
            frm.disable_save();
            frappe.show_alert({
                message: __('This document is archived and cannot be edited'),
                indicator: 'orange'
            });
        }
    },

    recipient_department: function (frm) {
        // Auto-fill department field
        if (frm.doc.recipient_department && !frm.doc.department) {
            frm.set_value('department', frm.doc.recipient_department);
        }

        // Auto-assign to department head
        if (frm.doc.recipient_department && !frm.doc.assigned_to) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Department',
                    filters: { name: frm.doc.recipient_department },
                    fieldname: 'department_head'
                },
                callback: function (r) {
                    if (r.message && r.message.department_head) {
                        frm.set_value('assigned_to', r.message.department_head);
                    }
                }
            });
        }
    },

    status: function (frm) {
        // Update SLA status when status changes
        if (frm.doc.status === 'Completed' || frm.doc.status === 'Archived') {
            frm.set_value('sla_status', 'On Track');
        }
    },

    before_save: function (frm) {
        // Calculate SLA status before save
        update_sla_status(frm);
    }
});

// Child table: Attachments
// Child table: Attachments
frappe.ui.form.on('Letter Attachment', {
    form_render: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.file) {
            update_attachment_preview(frm, cdt, cdn);
        }
    },

    file: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.file) {
            update_attachment_preview(frm, cdt, cdn);

            if (!row.ocr_extracted) {
                process_ocr_for_attachment(frm, row);
            }
        }
    }
});

function update_attachment_preview(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.file) {
        let file_url = row.file;
        let html = `<div class="btn-group">
            <button class="btn btn-xs btn-primary" onclick="cur_frm.events.preview_and_sign(cur_frm, '${cdt}', '${cdn}')">
                <i class="fa fa-pencil-square-o"></i> ${__('Preview & Sign')}
            </button>
            <a href="${file_url}" target="_blank" class="btn btn-xs btn-default">
                <i class="fa fa-external-link"></i>
            </a>
        </div>`;
        frappe.model.set_value(cdt, cdn, 'preview_html', html);
    }
}

frappe.ui.form.on('Incoming Letter', {
    preview_and_sign: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        new AttachmentPreview(frm, row).show();
    }
});

class AttachmentPreview {
    constructor(frm, row) {
        this.frm = frm;
        this.row = row;
        this.file_url = row.file;
        this.dialog = null;
        this.signature_pad = null;
        this.stamp_image = null; // Store the stamp image data
    }

    show() {
        this.dialog = new frappe.ui.Dialog({
            title: __('Preview, Sign & Stamp: ') + (this.row.file_name || 'Document'),
            size: 'extra-large',
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'preview_area'
                }
            ]
        });

        this.setup_preview();
        this.dialog.show();
    }

    setup_preview() {
        let html = `
            <div class="row" style="height: 75vh;">
                <div class="col-md-9 h-100">
                    <iframe src="${this.file_url}" style="width: 100%; height: 100%; border: none; background: #f0f0f0;"></iframe>
                </div>
                <div class="col-md-3 h-100" style="border-left: 1px solid #ddd; padding-left: 15px; overflow-y: auto;">
                    <h4>${__('Actions')}</h4>
                    
                    <!-- Signature Section -->
                    <div class="section-card" style="background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 15px;">
                        <h5><i class="fa fa-pencil"></i> ${__('Signature')}</h5>
                        <div class="form-group">
                            <button class="btn btn-default btn-sm btn-block" id="btn-show-sig-pad">
                                ${__('Draw Signature')}
                            </button>
                        </div>

                        <div id="signature-pad-container" style="display: none; margin-top: 10px;">
                            <canvas id="signature-pad" width="250" height="150" style="border: 1px solid #ccc; background: #fff; cursor: crosshair; touch-action: none;"></canvas>
                            <div class="mt-2 text-right">
                                <button class="btn btn-xs btn-default" id="btn-clear-sig">${__('Clear')}</button>
                            </div>
                            <div class="mt-2">
                                <label class="small">${__('Position')}</label>
                                <select class="form-control input-sm" id="sig-position">
                                    <option value="bottom-right">${__('Bottom Right')}</option>
                                    <option value="bottom-left">${__('Bottom Left')}</option>
                                    <option value="top-right">${__('Top Right')}</option>
                                </select>
                            </div>
                            <button class="btn btn-sm btn-primary btn-block mt-2" id="btn-apply-sig">${__('Apply Signature')}</button>
                        </div>
                    </div>

                    <!-- Stamp Section -->
                    <div class="section-card" style="background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 15px;">
                        <h5><i class="fa fa-certificate"></i> ${__('Company Stamp')}</h5>
                        <div class="form-group">
                            <button class="btn btn-default btn-sm btn-block" id="btn-upload-stamp">
                                ${__('Upload Stamp Image')}
                            </button>
                            <input type="file" id="stamp-file-input" accept="image/png" style="display: none;">
                        </div>

                        <div id="stamp-preview-container" style="display: none; margin-top: 10px; text-align: center;">
                            <img id="stamp-preview-img" src="" style="max-width: 100px; max-height: 100px; border: 1px dashed #ccc; padding: 5px;">
                            <div class="mt-2 text-left">
                                <label class="small">${__('Position')}</label>
                                <select class="form-control input-sm" id="stamp-position">
                                    <option value="bottom-center">${__('Bottom Center')}</option>
                                    <option value="bottom-right">${__('Bottom Right')}</option>
                                    <option value="bottom-left">${__('Bottom Left')}</option>
                                    <option value="top-right">${__('Top Right')}</option>
                                    <option value="top-left">${__('Top Left')}</option>
                                </select>
                            </div>
                            <button class="btn btn-sm btn-primary btn-block mt-2" id="btn-apply-stamp">${__('Apply Stamp')}</button>
                        </div>
                    </div>

                </div>
            </div>
        `;
        this.dialog.fields_dict.preview_area.$wrapper.html(html);

        this.bind_events();
    }

    bind_events() {
        let me = this;
        let $wrapper = this.dialog.fields_dict.preview_area.$wrapper;

        // Signature Events
        $wrapper.find('#btn-show-sig-pad').on('click', function () {
            $wrapper.find('#signature-pad-container').slideToggle();
            me.init_signature_pad();
        });

        $wrapper.find('#btn-clear-sig').on('click', function () {
            me.clear_signature();
        });

        $wrapper.find('#btn-apply-sig').on('click', function () {
            me.apply_signature();
        });

        // Stamp Events
        $wrapper.find('#btn-upload-stamp').on('click', function () {
            $wrapper.find('#stamp-file-input').click();
        });

        $wrapper.find('#stamp-file-input').on('change', function (e) {
            let file = e.target.files[0];
            if (file) {
                let reader = new FileReader();
                reader.onload = function (e) {
                    me.stamp_image = e.target.result;
                    $wrapper.find('#stamp-preview-img').attr('src', me.stamp_image);
                    $wrapper.find('#stamp-preview-container').slideDown();
                };
                reader.readAsDataURL(file);
            }
        });

        $wrapper.find('#btn-apply-stamp').on('click', function () {
            me.apply_stamp();
        });
    }

    init_signature_pad() {
        let canvas = this.dialog.fields_dict.preview_area.$wrapper.find('#signature-pad')[0];
        if (this.ctx) return; // Already initialized

        this.ctx = canvas.getContext('2d');
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.strokeStyle = '#000';

        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;

        const getCoords = (e) => {
            const rect = canvas.getBoundingClientRect();
            let clientX = e.clientX;
            let clientY = e.clientY;

            if (e.touches && e.touches.length > 0) {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            }

            return {
                x: clientX - rect.left,
                y: clientY - rect.top
            };
        };

        const startDrawing = (e) => {
            isDrawing = true;
            const coords = getCoords(e);
            lastX = coords.x;
            lastY = coords.y;
            e.preventDefault();
        };

        const draw = (e) => {
            if (!isDrawing) return;
            e.preventDefault();
            const coords = getCoords(e);

            this.ctx.beginPath();
            this.ctx.moveTo(lastX, lastY);
            this.ctx.lineTo(coords.x, coords.y);
            this.ctx.stroke();

            lastX = coords.x;
            lastY = coords.y;
        };

        const stopDrawing = () => {
            isDrawing = false;
        };

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mouseout', stopDrawing);

        // Touch support
        canvas.addEventListener('touchstart', startDrawing);
        canvas.addEventListener('touchmove', draw);
        canvas.addEventListener('touchend', stopDrawing);
    }

    clear_signature() {
        let canvas = this.dialog.fields_dict.preview_area.$wrapper.find('#signature-pad')[0];
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    apply_signature() {
        let me = this;
        let canvas = this.dialog.fields_dict.preview_area.$wrapper.find('#signature-pad')[0];

        // Check if empty
        let blank = document.createElement('canvas');
        blank.width = canvas.width;
        blank.height = canvas.height;
        if (canvas.toDataURL() === blank.toDataURL()) {
            frappe.msgprint(__('Please draw a signature first.'));
            return;
        }

        let signatureImage = canvas.toDataURL('image/png');
        let position = me.dialog.fields_dict.preview_area.$wrapper.find('#sig-position').val();

        me.process_pdf_edit(signatureImage, position, 'signature');
    }

    apply_stamp() {
        let me = this;
        if (!me.stamp_image) {
            frappe.msgprint(__('Please upload a stamp image first.'));
            return;
        }

        let position = me.dialog.fields_dict.preview_area.$wrapper.find('#stamp-position').val();
        me.process_pdf_edit(me.stamp_image, position, 'stamp');
    }

    process_pdf_edit(imageData, position, type) {
        let me = this;
        frappe.show_alert({ message: __('Processing document...'), indicator: 'blue' });

        // Load PDFLib
        frappe.require("https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js", async function () {
            try {
                const { PDFDocument } = PDFLib;

                // Fetch existing PDF
                const existingPdfBytes = await fetch(me.file_url).then(res => res.arrayBuffer());

                // Load a PDFDocument from the existing PDF bytes
                const pdfDoc = await PDFDocument.load(existingPdfBytes);

                // Embed the PNG image
                const pngImage = await pdfDoc.embedPng(imageData);

                // Get the first page of the document
                const pages = pdfDoc.getPages();
                const firstPage = pages[0]; // Apply to first page by default
                const { width, height } = firstPage.getSize();

                // Calculate position and size
                let x, y, imgWidth, imgHeight;
                const padding = 50;

                if (type === 'signature') {
                    imgWidth = 150;
                    imgHeight = (pngImage.height / pngImage.width) * imgWidth;
                } else {
                    // Stamp might be square or round, usually slightly larger
                    imgWidth = 120;
                    imgHeight = (pngImage.height / pngImage.width) * imgWidth;
                }

                if (position === 'bottom-right') {
                    x = width - imgWidth - padding;
                    y = padding;
                } else if (position === 'bottom-left') {
                    x = padding;
                    y = padding;
                } else if (position === 'top-right') {
                    x = width - imgWidth - padding;
                    y = height - imgHeight - padding;
                } else if (position === 'top-left') {
                    x = padding;
                    y = height - imgHeight - padding;
                } else if (position === 'bottom-center') {
                    x = (width - imgWidth) / 2;
                    y = padding;
                }

                // Draw the PNG image onto the page
                firstPage.drawImage(pngImage, {
                    x: x,
                    y: y,
                    width: imgWidth,
                    height: imgHeight,
                });

                // Serialize the PDFDocument to bytes (a Uint8Array)
                const pdfBytes = await pdfDoc.save();

                // Upload the file
                me.upload_signed_file(pdfBytes);

            } catch (e) {
                console.error(e);
                frappe.msgprint(__('Error processing document: ') + e.message);
            }
        });
    }

    upload_signed_file(pdfBytes) {
        let me = this;
        let file = new File([pdfBytes], 'processed_' + (me.row.file_name || 'document.pdf'), { type: "application/pdf" });

        let formData = new FormData();
        formData.append('file', file);
        formData.append('is_private', 0);
        formData.append('folder', 'Home');

        // Using XHR for file upload
        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/method/upload_file');
        xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);

        xhr.onload = function () {
            if (xhr.status === 200) {
                let response = JSON.parse(xhr.responseText);
                if (response.message) {
                    let file_doc = response.message;

                    // Update the attachment row
                    frappe.model.set_value(me.row.doctype, me.row.name, 'file', file_doc.file_url);
                    frappe.model.set_value(me.row.doctype, me.row.name, 'file_name', file_doc.file_name);

                    me.dialog.hide();
                    frappe.show_alert({ message: __('Document updated successfully'), indicator: 'green' });
                }
            } else {
                frappe.msgprint(__('Upload failed'));
            }
        };

        xhr.send(formData);
    }
}

function add_custom_buttons(frm) {
    if (!frm.is_new()) {
        // Refresh Related Documents button
        frm.add_custom_button(__('Refresh Related Documents'), function () {
            refresh_related_documents(frm);
        }, __('Actions'));

        // Archive button
        if (!frm.doc.is_archived && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Archive'), function () {
                archive_document(frm);
            }, __('Actions'));
        }

        // Unarchive button (System Manager only)
        if (frm.doc.is_archived && frappe.user.has_role('System Manager')) {
            frm.add_custom_button(__('Unarchive'), function () {
                unarchive_document(frm);
            }, __('Actions'));
        }

        // Find Similar Documents
        frm.add_custom_button(__('Find Similar'), function () {
            find_similar_documents(frm);
        }, __('Actions'));

        // Process OCR for all attachments
        if (frm.doc.attachments && frm.doc.attachments.length > 0) {
            frm.add_custom_button(__('Process OCR'), function () {
                process_all_ocr(frm);
            }, __('Actions'));
        }

        // Auto-categorize
        frm.add_custom_button(__('Auto-Categorize'), function () {
            auto_categorize_document(frm);
        }, __('Actions'));
    }
}

function show_related_documents_panel(frm) {
    // Create a custom section to show related documents
    if (frm.doc.related_documents && frm.doc.related_documents.length > 0) {
        let html = '<div class="related-documents-panel" style="margin-top: 15px;">';
        html += '<h4>Related Documents</h4>';
        html += '<table class="table table-bordered">';
        html += '<thead><tr><th>Document</th><th>Similarity</th><th>Action</th></tr></thead>';
        html += '<tbody>';

        frm.doc.related_documents.forEach(function (doc) {
            let score = doc.similarity_score ? (doc.similarity_score * 100).toFixed(0) + '%' : 'N/A';
            html += `<tr>
				<td>${doc.document_type}: ${doc.document_name}</td>
				<td><span class="badge badge-info">${score}</span></td>
				<td><a href="/app/${doc.document_type.toLowerCase().replace(' ', '-')}/${doc.document_name}" target="_blank">Open</a></td>
			</tr>`;
        });

        html += '</tbody></table></div>';

        // Add to form
        frm.fields_dict['related_documents_section'].$wrapper.append(html);
    }
}

function show_version_history_button(frm) {
    frm.add_custom_button(__('Version History'), function () {
        show_version_history_dialog(frm);
    }, __('View'));
}

function show_version_history_dialog(frm) {
    frappe.call({
        method: 'correspondence.correspondence.utils.version_control.get_version_history_api',
        args: {
            doctype: frm.doctype,
            docname: frm.docname
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                let versions = r.message.versions;

                let dialog = new frappe.ui.Dialog({
                    title: __('Version History'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'version_html'
                        }
                    ],
                    size: 'large'
                });

                let html = '<table class="table table-bordered">';
                html += '<thead><tr><th>Version</th><th>Editor</th><th>Date</th><th>Changes</th><th>Current</th><th>Action</th></tr></thead>';
                html += '<tbody>';

                versions.forEach(function (v) {
                    html += `<tr>
						<td>v${v.version_number}</td>
						<td>${v.editor}</td>
						<td>${frappe.datetime.str_to_user(v.created_on)}</td>
						<td>${v.changes_summary || '-'}</td>
						<td>${v.is_current ? '<span class="badge badge-success">Current</span>' : ''}</td>
						<td><a href="${v.original_file}" target="_blank">Download</a></td>
					</tr>`;
                });

                html += '</tbody></table>';

                dialog.fields_dict.version_html.$wrapper.html(html);
                dialog.show();
            }
        }
    });
}

function archive_document(frm) {
    frappe.confirm(
        __('Are you sure you want to archive this document? It will become read-only.'),
        function () {
            frappe.call({
                method: 'correspondence.correspondence.api.archive.archive_document',
                args: {
                    doctype: frm.doctype,
                    docname: frm.docname
                },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Document archived successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('Archive failed: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    );
}

function unarchive_document(frm) {
    frappe.confirm(
        __('Are you sure you want to unarchive this document?'),
        function () {
            frappe.call({
                method: 'correspondence.correspondence.api.archive.unarchive_document',
                args: {
                    doctype: frm.doctype,
                    docname: frm.docname
                },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __('Document unarchived successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('Unarchive failed: ') + (r.message.error || 'Unknown error'));
                    }
                }
            });
        }
    );
}

function find_similar_documents(frm) {
    frappe.call({
        method: 'correspondence.correspondence.utils.similarity_engine.get_similar_documents',
        args: {
            doctype: frm.doctype,
            docname: frm.docname
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                let docs = r.message.documents;

                if (docs.length === 0) {
                    frappe.msgprint(__('No similar documents found'));
                    return;
                }

                let dialog = new frappe.ui.Dialog({
                    title: __('Similar Documents'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'similar_html'
                        }
                    ],
                    size: 'large'
                });

                let html = '<table class="table table-bordered">';
                html += '<thead><tr><th>Document</th><th>Subject</th><th>Similarity</th><th>Action</th></tr></thead>';
                html += '<tbody>';

                docs.forEach(function (doc) {
                    let score = (doc.score * 100).toFixed(0) + '%';
                    html += `<tr>
						<td>${doc.doctype}<br/><small>${doc.name}</small></td>
						<td>${doc.subject}</td>
						<td><span class="badge badge-info">${score}</span></td>
						<td><a href="/app/${doc.doctype.toLowerCase().replace(' ', '-')}/${doc.name}" target="_blank">Open</a></td>
					</tr>`;
                });

                html += '</tbody></table>';

                dialog.fields_dict.similar_html.$wrapper.html(html);
                dialog.show();
            }
        }
    });
}

function process_ocr_for_attachment(frm, row) {
    frappe.show_alert({
        message: __('Processing OCR...'),
        indicator: 'blue'
    });

    frappe.call({
        method: 'correspondence.correspondence.utils.ocr_processor.process_file_ocr',
        args: {
            file_url: row.file
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                frappe.model.set_value(row.doctype, row.name, 'ocr_text', r.message.text);
                frappe.model.set_value(row.doctype, row.name, 'ocr_extracted', 1);

                frappe.show_alert({
                    message: __('OCR completed'),
                    indicator: 'green'
                });
            }
        }
    });
}

function process_all_ocr(frm) {
    frappe.confirm(
        __('Process OCR for all attachments?'),
        function () {
            let file_urls = frm.doc.attachments.map(a => a.file);

            frappe.call({
                method: 'correspondence.correspondence.utils.ocr_processor.batch_process_ocr',
                args: {
                    file_urls: file_urls
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('OCR processing completed'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function auto_categorize_document(frm) {
    frappe.call({
        method: 'correspondence.correspondence.utils.topic_classifier.classify_document_api',
        args: {
            doctype: frm.doctype,
            docname: frm.docname
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                let topics = r.message.topics;

                if (topics.length === 0) {
                    frappe.msgprint(__('No topics suggested'));
                    return;
                }

                frappe.confirm(
                    __('Apply suggested topics: ') + topics.join(', ') + '?',
                    function () {
                        frappe.call({
                            method: 'correspondence.correspondence.utils.topic_classifier.apply_topics_to_document',
                            args: {
                                doctype: frm.doctype,
                                docname: frm.docname,
                                topics: topics
                            },
                            callback: function (r) {
                                if (r.message && r.message.success) {
                                    frappe.show_alert({
                                        message: __('Topics applied successfully'),
                                        indicator: 'green'
                                    });
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            }
        }
    });
}

function update_sla_status(frm) {
    if (!frm.doc.due_date) {
        return;
    }

    let today = frappe.datetime.get_today();
    let due_date = frm.doc.due_date;

    if (frm.doc.status === 'Completed' || frm.doc.status === 'Archived') {
        frm.set_value('sla_status', 'On Track');
    } else if (due_date < today) {
        frm.set_value('sla_status', 'Overdue');
    } else {
        let days_diff = frappe.datetime.get_day_diff(due_date, today);
        if (days_diff <= 2) {
            frm.set_value('sla_status', 'At Risk');
        } else {
            frm.set_value('sla_status', 'On Track');
        }
    }
}

function refresh_related_documents(frm, silent = false) {
    if (!silent) {
        frappe.show_alert({
            message: __('Searching for related documents...'),
            indicator: 'blue'
        });
    }

    // If document is dirty or new, use preview API
    if (frm.is_dirty() || frm.is_new()) {
        frappe.call({
            method: 'correspondence.correspondence.utils.auto_relation_finder.preview_related_documents',
            args: {
                doctype: frm.doctype,
                doc_data: JSON.stringify(frm.doc)
            },
            callback: function (r) {
                if (r.message && r.message.success) {
                    let related_docs = r.message.related_documents;

                    // Clear existing auto relations
                    let manual_relations = (frm.doc.related_documents || []).filter(d => d.relation_type === 'Manual');
                    frm.clear_table('related_documents');

                    // Add manual relations back
                    manual_relations.forEach(d => {
                        let row = frm.add_child('related_documents');
                        Object.assign(row, d);
                    });

                    // Add new auto relations
                    related_docs.forEach(d => {
                        let row = frm.add_child('related_documents');
                        row.document_type = d.doctype;
                        row.document_name = d.name;
                        row.similarity_score = d.score;
                        row.relation_type = 'Auto';
                        row.notes = d.relation_reason;
                    });

                    frm.refresh_field('related_documents');
                    show_related_documents_panel(frm);

                    if (!silent) {
                        frappe.show_alert({
                            message: __(r.message.message),
                            indicator: 'green'
                        }, 5);
                    }
                }
            }
        });
    } else {
        // Use standard refresh API for saved documents
        frappe.call({
            method: 'correspondence.correspondence.utils.auto_relation_finder.refresh_related_documents',
            args: {
                doctype: frm.doctype,
                docname: frm.docname
            },
            callback: function (r) {
                if (r.message && r.message.success) {
                    frm.reload_doc();

                    if (!silent) {
                        frappe.show_alert({
                            message: __(r.message.message),
                            indicator: 'green'
                        }, 5);
                    }
                } else {
                    if (!silent) {
                        frappe.show_alert({
                            message: __('Failed to refresh related documents'),
                            indicator: 'red'
                        }, 5);
                    }
                }
            }
        });
    }
}
