// Client Script for Incoming Letter
// Enhances UI with auto-fill, related documents panel, and OCR processing

frappe.ui.form.on('Incoming Letter', {
    refresh: function (frm) {
        // Add "View and Assign" button
        if (!frm.is_new()) {
            frm.add_custom_button(__('View and Assign'), function () {
                show_view_and_assign_dialog(frm);
            }, __('Actions'));
        }

        // Check for digital signature
        if (!frm.is_new()) {
            frappe.call({
                method: 'correspondence.correspondence.utils.digital_signature.get_document_signatures',
                args: { doctype: frm.doctype, docname: frm.docname },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        // Show signed badge
                        frm.dashboard.add_indicator(__('Signed'), 'green');

                        // Add verify button
                        frm.add_custom_button(__('Verify Signature'), function () {
                            let signatures = r.message;
                            let html = `
                                <div style="padding: 10px;">
                                    <table class="table table-bordered">
                                        <thead>
                                            <tr>
                                                <th>${__('Signer')}</th>
                                                <th>${__('Date')}</th>
                                                <th>${__('Status')}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${signatures.map(sig => `
                                                <tr>
                                                    <td>${sig.signer}</td>
                                                    <td>${frappe.datetime.str_to_user(sig.signature_date)}</td>
                                                    <td><span class="indicator green">${__('Valid')}</span></td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            `;

                            frappe.msgprint({
                                title: __('Digital Signatures'),
                                message: html,
                                wide: true
                            });
                        }, __('Actions'));
                    }
                }
            });
        }

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

        // New Features for v1.0.1

        // Digital Signature - Generate Keys
        frm.add_custom_button(__('Generate Signature Keys'), function () {
            frappe.confirm(
                __('This will generate new signature keys for you. Continue?'),
                function () {
                    frappe.call({
                        method: 'correspondence.correspondence.utils.digital_signature.generate_user_keys',
                        callback: function (r) {
                            if (r.message && r.message.success) {
                                frappe.msgprint({
                                    title: __('Success'),
                                    message: __('Signature keys generated successfully. You can now sign documents.'),
                                    indicator: 'green'
                                });
                            }
                        }
                    });
                }
            );
        }, __('Actions'));

        // Digital Signature - Sign Document
        frm.add_custom_button(__('Sign Document'), function () {
            frappe.call({
                method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
                args: { doctype: frm.doctype, docname: frm.docname },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Document signed successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else if (r.exc) {
                        // Check if error is about missing keys
                        if (r._server_messages) {
                            let messages = JSON.parse(r._server_messages);
                            if (messages && messages.length > 0) {
                                let msg = JSON.parse(messages[0]);
                                if (msg.message && msg.message.includes('No signature keys found')) {
                                    frappe.msgprint({
                                        title: __('Keys Required'),
                                        message: __('Please generate signature keys first by clicking "Generate Signature Keys" button.'),
                                        indicator: 'orange'
                                    });
                                }
                            }
                        }
                    }
                }
            });
        }, __('Actions'));

        // Generate QR Code for Letter Tracking
        frm.add_custom_button(__('Generate Tracking QR'), function () {
            frappe.call({
                method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
                args: {
                    doctype: frm.doctype,
                    docname: frm.docname,
                    include_metadata: 1
                },
                callback: function (r) {
                    if (r.message && r.message.success) {
                        // Save QR code as base64 data URL to the document
                        let qr_data_url = 'data:image/png;base64,' + r.message.qr_image;

                        // Upload as file and attach to document
                        upload_base64_image(qr_data_url, frm.docname + '_tracking_qr.png', function (file_url) {
                            frm.set_value('qr_code_image', file_url);
                            frm.save();
                            frappe.show_alert({
                                message: __('Tracking QR Code generated and saved'),
                                indicator: 'green'
                            });
                        });
                    }
                }
            });
        }, __('Actions'));


        // Analytics Dashboard
        frm.add_custom_button(__('Analytics'), function () {
            frappe.call({
                method: 'correspondence.correspondence.utils.ml_analytics.get_analytics_dashboard',
                args: { doctype: frm.doctype },
                callback: function (r) {
                    if (r.message) {
                        show_analytics_dashboard(r.message);
                    } else {
                        frappe.msgprint(__('Unable to load analytics data'));
                    }
                },
                error: function (r) {
                    frappe.msgprint(__('Error loading analytics: ') + (r.message || 'Unknown error'));
                }
            });
        }, __('View'));

        // Voice to Text
        frm.add_custom_button(__('Voice to Text'), function () {
            show_voice_to_text_dialog(frm);
        }, __('Actions'));
    }
}

function show_voice_to_text_dialog(frm) {
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    let d = new frappe.ui.Dialog({
        title: __('Convert Audio to Text'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'instructions',
                options: `<p class="text-muted">${__('Choose to record live or upload an audio file.')}</p>`
            },
            {
                fieldtype: 'Select',
                fieldname: 'input_method',
                label: __('Input Method'),
                options: 'Record Live\nUpload File',
                default: 'Record Live',
                onchange: function () {
                    let method = d.get_value('input_method');
                    if (method === 'Record Live') {
                        d.fields_dict.audio_file.$wrapper.hide();
                        d.fields_dict.recording_controls.$wrapper.show();
                    } else {
                        d.fields_dict.audio_file.$wrapper.show();
                        d.fields_dict.recording_controls.$wrapper.hide();
                    }
                }
            },
            {
                fieldtype: 'HTML',
                fieldname: 'recording_controls',
                options: `
                    <div class="recording-controls" style="margin: 15px 0;">
                        <button class="btn btn-primary btn-sm" id="start-recording">
                            <i class="fa fa-microphone"></i> ${__('Start Recording')}
                        </button>
                        <button class="btn btn-danger btn-sm" id="stop-recording" style="display: none;">
                            <i class="fa fa-stop"></i> ${__('Stop Recording')}
                        </button>
                        <div id="recording-status" style="margin-top: 10px; display: none;">
                            <span class="indicator red"></span>
                            <span>${__('Recording...')}</span>
                            <span id="recording-timer">00:00</span>
                        </div>
                        <audio id="audio-preview" controls style="width: 100%; margin-top: 10px; display: none;"></audio>
                    </div>
                `
            },
            {
                fieldtype: 'Attach',
                fieldname: 'audio_file',
                label: __('Audio File'),
                hidden: 1
            },
            {
                fieldtype: 'Select',
                fieldname: 'language',
                label: __('Language'),
                options: 'en-US\nar-SA\nfr-FR\nde-DE\nes-ES\nit-IT\nzh-CN\nja-JP',
                default: 'en-US'
            },
            {
                fieldtype: 'Select',
                fieldname: 'target_field',
                label: __('Insert Into'),
                options: frm.doctype === 'Incoming Letter' ? 'Summary\nOCR Text' : 'Body Text\nOCR Text',
                default: frm.doctype === 'Incoming Letter' ? 'Summary' : 'Body Text'
            }
        ],
        primary_action_label: __('Convert'),
        primary_action: function (values) {
            let audioFile = values.audio_file;
            let audioBlob = null;

            // Check if we have a recorded audio
            if (values.input_method === 'Record Live' && audioChunks.length > 0) {
                audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            } else if (values.input_method === 'Upload File' && !audioFile) {
                frappe.msgprint(__('Please upload an audio file'));
                return;
            } else if (values.input_method === 'Record Live' && audioChunks.length === 0) {
                frappe.msgprint(__('Please record audio first'));
                return;
            }

            frappe.show_alert({
                message: __('Converting audio to text...'),
                indicator: 'blue'
            });

            // If we have a blob, upload it first
            if (audioBlob) {
                let formData = new FormData();
                formData.append('file', audioBlob, 'recording.webm');
                formData.append('is_private', 0);
                formData.append('folder', 'Home');

                let xhr = new XMLHttpRequest();
                xhr.open('POST', '/api/method/upload_file');
                xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        let response = JSON.parse(xhr.responseText);
                        if (response.message) {
                            audioFile = response.message.file_url;
                            convertAudio(audioFile, values, frm, d);
                        }
                    } else {
                        frappe.msgprint(__('Upload failed'));
                    }
                };

                xhr.send(formData);
            } else {
                convertAudio(audioFile, values, frm, d);
            }
        }
    });

    d.show();

    // Setup recording controls
    setTimeout(() => {
        let $startBtn = d.$wrapper.find('#start-recording');
        let $stopBtn = d.$wrapper.find('#stop-recording');
        let $status = d.$wrapper.find('#recording-status');
        let $preview = d.$wrapper.find('#audio-preview');
        let $timer = d.$wrapper.find('#recording-timer');
        let startTime = null;
        let timerInterval = null;

        $startBtn.on('click', async function () {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    $preview[0].src = audioUrl;
                    $preview.show();
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                isRecording = true;
                $startBtn.hide();
                $stopBtn.show();
                $status.show();
                $preview.hide();

                // Start timer
                startTime = Date.now();
                timerInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
                    const seconds = (elapsed % 60).toString().padStart(2, '0');
                    $timer.text(`${minutes}:${seconds}`);
                }, 1000);

            } catch (err) {
                frappe.msgprint(__('Microphone access denied. Please allow microphone access.'));
            }
        });

        $stopBtn.on('click', function () {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                $startBtn.show();
                $stopBtn.hide();
                $status.hide();
                clearInterval(timerInterval);
            }
        });
    }, 500);
}

function convertAudio(audioFile, values, frm, dialog) {
    frappe.call({
        method: 'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
        args: {
            file_url: audioFile,
            language: values.language || 'en-US'
        },
        callback: function (r) {
            if (r.message && r.message.success) {
                let text = r.message.text;

                // Insert into selected field
                if (frm.doctype === 'Incoming Letter') {
                    if (values.target_field === 'Summary') {
                        let current = frm.doc.summary || '';
                        frm.set_value('summary', current + (current ? '\n\n' : '') + text);
                    } else {
                        let current = frm.doc.ocr_text || '';
                        frm.set_value('ocr_text', current + (current ? '\n\n' : '') + text);
                    }
                } else {
                    if (values.target_field === 'Body Text') {
                        let current = frm.doc.body_text || '';
                        frm.set_value('body_text', current + (current ? '\n\n' : '') + text);
                    } else {
                        let current = frm.doc.ocr_text || '';
                        frm.set_value('ocr_text', current + (current ? '\n\n' : '') + text);
                    }
                }

                frappe.show_alert({
                    message: __('Audio converted successfully'),
                    indicator: 'green'
                });

                dialog.hide();
            } else {
                frappe.msgprint({
                    title: __('Conversion Failed'),
                    message: r.message ? r.message.message : __('Failed to convert audio'),
                    indicator: 'red'
                });
            }
        },
        error: function (r) {
            frappe.msgprint({
                title: __('Error'),
                message: __('An error occurred during conversion'),
                indicator: 'red'
            });
        }
    });
}

function show_analytics_dashboard(data) {
    let d = new frappe.ui.Dialog({
        title: __('Analytics Dashboard'),
        size: 'large',
        fields: [{ fieldtype: 'HTML', fieldname: 'html' }]
    });

    // Handle cases where data might be missing
    let trends = (data.trends && data.trends.success && data.trends.trends) ? data.trends.trends : null;
    let insights = (data.insights && data.insights.insights) ? data.insights.insights : [];
    let bottlenecks = (data.bottlenecks && data.bottlenecks.bottlenecks) ? data.bottlenecks.bottlenecks : [];

    let html = '';

    // Trends section
    if (trends) {
        html += `
        <div class="row">
            <div class="col-md-4">
                <div class="dashboard-stat-box">
                    <h4>${trends.total_letters || 0}</h4>
                    <span class="text-muted">${__('Total Letters')}</span>
                </div>
            </div>
            <div class="col-md-4">
                <div class="dashboard-stat-box">
                    <h4>${trends.daily_average || 0}</h4>
                    <span class="text-muted">${__('Daily Average')}</span>
                </div>
            </div>
            <div class="col-md-4">
                <div class="dashboard-stat-box">
                    <h4 class="${(trends.growth_rate || 0) >= 0 ? 'text-success' : 'text-danger'}">
                        ${trends.growth_rate || 0}%
                    </h4>
                    <span class="text-muted">${__('Growth Rate')}</span>
                </div>
            </div>
        </div>
        <hr>`;
    } else {
        html += `
        <div class="alert alert-info">
            <strong>${__('No trend data available')}</strong><br>
            ${data.trends && data.trends.message ? data.trends.message : __('Insufficient data for the specified period')}
        </div>
        <hr>`;
    }

    // Insights and Bottlenecks section
    html += `
        <div class="row mt-3">
            <div class="col-md-6">
                <h5>${__('Insights')}</h5>
                <ul class="list-group">
                    ${insights.map(i => `
                        <li class="list-group-item list-group-item-${i.severity === 'high' ? 'danger' : (i.severity === 'medium' ? 'warning' : 'info')}">
                            ${i.message}
                        </li>
                    `).join('')}
                    ${insights.length === 0 ? `<li class="list-group-item text-muted">${__('No insights available')}</li>` : ''}
                </ul>
            </div>
            <div class="col-md-6">
                <h5>${__('Bottlenecks')}</h5>
                <ul class="list-group">
                    ${bottlenecks.map(b => `
                        <li class="list-group-item">
                            <strong>${b.name}</strong>: ${b.pending_count || b.count} ${__('pending')}
                            <span class="badge badge-${b.severity === 'high' ? 'danger' : 'warning'} float-right">${b.severity}</span>
                        </li>
                    `).join('')}
                    ${bottlenecks.length === 0 ? `<li class="list-group-item text-muted">${__('No bottlenecks detected')}</li>` : ''}
                </ul>
            </div>
        </div>
    `;

    d.fields_dict.html.$wrapper.html(html);
    d.show();
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
                    frappe.msgprint({
                        title: __('No Similar Documents'),
                        message: __('No similar documents were found. This could be because:<br>1. There are no other documents with similar content<br>2. The current document lacks sufficient content (subject, summary, or body text)<br>3. Try adding more descriptive content to improve similarity matching'),
                        indicator: 'orange'
                    });
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
            } else {
                // Show error message
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message && r.message.error ? r.message.error : __('Failed to find similar documents'),
                    indicator: 'red'
                });
            }
        },
        error: function (r) {
            frappe.msgprint({
                title: __('Error'),
                message: __('An error occurred while searching for similar documents'),
                indicator: 'red'
            });
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

// Helper function to upload base64 image
function upload_base64_image(data_url, filename, callback) {
    // Convert base64 to blob
    fetch(data_url)
        .then(res => res.blob())
        .then(blob => {
            let file = new File([blob], filename, { type: 'image/png' });
            let formData = new FormData();
            formData.append('file', file);
            formData.append('is_private', 0);
            formData.append('folder', 'Home');

            // Upload using XHR
            let xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/method/upload_file');
            xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    let response = JSON.parse(xhr.responseText);
                    if (response.message && callback) {
                        callback(response.message.file_url);
                    }
                } else {
                    frappe.msgprint(__('Upload failed'));
                }
            };

            xhr.send(formData);
        });
}

// Function to show View and Assign Dialog for Incoming Letters
function show_view_and_assign_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('View and Assign Letter'),
        size: 'large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'letter_details',
                options: get_letter_details_html(frm)
            },
            {
                fieldtype: 'Section Break',
                label: __('Assignment')
            },
            {
                fieldtype: 'Link',
                fieldname: 'assigned_to',
                label: __('Assign To'),
                options: 'User',
                default: frm.doc.assigned_to || ''
            },
            {
                fieldtype: 'Column Break'
            },
            {
                fieldtype: 'Date',
                fieldname: 'due_date',
                label: __('Due Date'),
                default: frm.doc.due_date || ''
            },
            {
                fieldtype: 'Section Break'
            },
            {
                fieldtype: 'Small Text',
                fieldname: 'assignment_note',
                label: __('Assignment Note'),
                description: __('Optional note for the assigned user')
            }
        ],
        primary_action_label: __('Assign'),
        primary_action: function (values) {
            if (!values.assigned_to) {
                frappe.msgprint(__('Please select a user to assign'));
                return;
            }

            // Update the document
            frm.set_value('assigned_to', values.assigned_to);
            if (values.due_date) {
                frm.set_value('due_date', values.due_date);
            }

            // Save the document
            frm.save().then(() => {
                // Create an assignment notification
                frappe.call({
                    method: 'frappe.desk.form.assign_to.add',
                    args: {
                        doctype: frm.doctype,
                        name: frm.docname,
                        assign_to: [values.assigned_to],
                        description: values.assignment_note || __('Letter assigned to you'),
                        title: frm.doc.subject || __('Incoming Letter Assignment')
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            frappe.show_alert({
                                message: __('Letter assigned successfully'),
                                indicator: 'green'
                            });
                            d.hide();
                            frm.reload_doc();
                        }
                    }
                });
            });
        },
        secondary_action_label: __('Close'),
        secondary_action: function () {
            d.hide();
        }
    });

    d.show();
}

// Helper function to generate letter details HTML
function get_letter_details_html(frm) {
    let doc = frm.doc;

    // Status color mapping
    let status_colors = {
        'New': 'blue',
        'Under Process': 'orange',
        'Waiting': 'yellow',
        'Completed': 'green',
        'Archived': 'gray'
    };

    // Priority color mapping
    let priority_colors = {
        'Low': 'gray',
        'Medium': 'blue',
        'High': 'orange',
        'Urgent': 'red'
    };

    let html = `
        <div style="padding: 15px; background: #f9f9f9; border-radius: 8px; margin-bottom: 15px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p style="margin: 5px 0;">
                        <strong>${__('Letter Number')}:</strong> 
                        <span style="color: #2490ef;">${doc.letter_number || doc.name}</span>
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Sender')}:</strong> 
                        ${doc.sender || '-'}
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Sender Organization')}:</strong> 
                        ${doc.sender_organization || '-'}
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Date Received')}:</strong> 
                        ${frappe.datetime.str_to_user(doc.date_received) || '-'}
                    </p>
                </div>
                <div>
                    <p style="margin: 5px 0;">
                        <strong>${__('Status')}:</strong> 
                        <span class="indicator-pill ${status_colors[doc.status] || 'gray'}">${__(doc.status)}</span>
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Priority')}:</strong> 
                        <span class="indicator-pill ${priority_colors[doc.priority] || 'gray'}">${__(doc.priority)}</span>
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Department')}:</strong> 
                        ${doc.recipient_department || '-'}
                    </p>
                    <p style="margin: 5px 0;">
                        <strong>${__('Currently Assigned To')}:</strong> 
                        ${doc.assigned_to ? `<span style="color: #2490ef;">${doc.assigned_to}</span>` : '<span style="color: #999;">${__("Not Assigned")}</span>'}
                    </p>
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                <p style="margin: 5px 0;">
                    <strong>${__('Subject')}:</strong>
                </p>
                <p style="margin: 5px 0; padding: 10px; background: white; border-radius: 4px;">
                    ${doc.subject || '-'}
                </p>
            </div>

            ${doc.summary ? `
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                <p style="margin: 5px 0;">
                    <strong>${__('Summary')}:</strong>
                </p>
                <div style="margin: 5px 0; padding: 10px; background: white; border-radius: 4px; max-height: 150px; overflow-y: auto;">
                    ${doc.summary}
                </div>
            </div>
            ` : ''}

            ${doc.attachments && doc.attachments.length > 0 ? `
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                <p style="margin: 5px 0;">
                    <strong>${__('Attachments')}:</strong> 
                    <span class="badge">${doc.attachments.length}</span>
                </p>
                <div style="margin-top: 10px;">
                    ${doc.attachments.map(att => `
                        <div style="margin: 5px 0;">
                            <a href="${att.file}" target="_blank" style="color: #2490ef;">
                                <i class="fa fa-file"></i> ${att.file_name || 'Attachment'}
                            </a>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    return html;
}
