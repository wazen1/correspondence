# Quick Reference Guide - Version 1.0.1 Features

A quick reference for developers integrating the new features.

## Digital Signatures

### Generate Keys (One-time setup)
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.generate_user_keys',
  callback: (r) => console.log(r.message)
});
```

### Sign Document
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
  args: { doctype: 'Incoming Letter', docname: 'INC-001' },
  callback: (r) => console.log('Signed:', r.message.signature)
});
```

### Verify Signature
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.verify_document_signature',
  args: { doctype: 'Incoming Letter', docname: 'INC-001' },
  callback: (r) => console.log('Valid:', r.message.is_valid)
});
```

---

## QR Codes & Barcodes

### Generate QR Code
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
  args: { 
    doctype: 'Incoming Letter', 
    docname: 'INC-001',
    include_metadata: 1 
  },
  callback: (r) => {
    let img = `<img src="data:image/png;base64,${r.message.qr_image}" />`;
    frappe.msgprint(img);
  }
});
```

### Generate Barcode
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.barcode_qr.generate_barcode_api',
  args: { 
    doctype: 'Incoming Letter', 
    docname: 'INC-001',
    barcode_type: 'code128'
  },
  callback: (r) => console.log('Barcode:', r.message.barcode_image)
});
```

### Scan QR Code
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.barcode_qr.scan_qr_code',
  args: { qr_data: '{"doctype":"Incoming Letter","name":"INC-001"}' },
  callback: (r) => {
    if (r.message.success) {
      frappe.set_route('Form', r.message.document.doctype, r.message.document.name);
    }
  }
});
```

---

## Analytics

### Predict Response Time
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.predict_response_time_api',
  args: { doctype: 'Incoming Letter', docname: 'INC-001' },
  callback: (r) => {
    console.log(`Expected in ${r.message.predicted_response_days} days`);
    console.log(`By: ${r.message.expected_response_date}`);
  }
});
```

### Predict Priority
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.predict_priority_api',
  args: { doctype: 'Incoming Letter', docname: 'INC-001' },
  callback: (r) => {
    console.log(`Priority: ${r.message.predicted_priority}`);
    console.log(`Confidence: ${r.message.confidence}%`);
  }
});
```

### Analyze Trends
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.analyze_trends_api',
  args: { doctype: 'Incoming Letter', period_days: 30 },
  callback: (r) => {
    console.log('Total:', r.message.trends.total_letters);
    console.log('Daily Avg:', r.message.trends.daily_average);
    console.log('Growth:', r.message.trends.growth_rate + '%');
  }
});
```

### Identify Bottlenecks
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.identify_bottlenecks_api',
  args: { doctype: 'Incoming Letter' },
  callback: (r) => {
    r.message.bottlenecks.forEach(b => {
      console.log(`${b.type}: ${b.name} (${b.severity})`);
    });
  }
});
```

### Generate Insights
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.generate_insights_api',
  args: { doctype: 'Incoming Letter' },
  callback: (r) => {
    r.message.insights.forEach(i => {
      console.log(`[${i.severity}] ${i.message}`);
    });
  }
});
```

### Complete Dashboard
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.get_analytics_dashboard',
  args: { doctype: 'Incoming Letter' },
  callback: (r) => {
    console.log('Trends:', r.message.trends);
    console.log('Bottlenecks:', r.message.bottlenecks);
    console.log('Insights:', r.message.insights);
  }
});
```

---

## Voice-to-Text

### Convert Audio to Text
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
  args: { 
    file_url: '/files/recording.wav',
    language: 'en-US'
  },
  callback: (r) => console.log('Text:', r.message.text)
});
```

### Create Letter from Voice
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.voice_to_text.create_letter_from_voice_api',
  args: { 
    file_url: '/files/recording.wav',
    doctype: 'Incoming Letter',
    language: 'en-US',
    metadata: JSON.stringify({
      department: 'Sales',
      priority: 'High'
    })
  },
  callback: (r) => {
    if (r.message.success) {
      frappe.set_route('Form', 'Incoming Letter', r.message.letter_name);
    }
  }
});
```

### Get Supported Languages
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.voice_to_text.get_supported_languages',
  callback: (r) => {
    Object.entries(r.message.languages).forEach(([code, name]) => {
      console.log(`${code}: ${name}`);
    });
  }
});
```

---

## Python Examples

### Digital Signature (Server-side)
```python
from correspondence.correspondence.utils.digital_signature import DigitalSignatureManager

manager = DigitalSignatureManager()

# Generate keys
keys = manager.generate_key_pair('user@example.com')

# Sign document
signature = manager.sign_document('Incoming Letter', 'INC-001', keys['private_key'], 'user@example.com')

# Verify signature
is_valid = manager.verify_signature('Incoming Letter', 'INC-001', signature, keys['public_key'])
```

### QR Code (Server-side)
```python
from correspondence.correspondence.utils.barcode_qr import BarcodeQRGenerator

generator = BarcodeQRGenerator()

# Generate QR code
qr_image = generator.generate_qr_code('Incoming Letter', 'INC-001', include_metadata=True)

# Generate barcode
barcode_image = generator.generate_barcode('Incoming Letter', 'INC-001', 'code128')
```

### Analytics (Server-side)
```python
from correspondence.correspondence.utils.ml_analytics import CorrespondenceAnalytics

analytics = CorrespondenceAnalytics()

# Predict response time
prediction = analytics.predict_response_time('Incoming Letter', 'INC-001')

# Analyze trends
trends = analytics.analyze_trends('Incoming Letter', period_days=30)

# Identify bottlenecks
bottlenecks = analytics.identify_bottlenecks('Incoming Letter')
```

### Voice-to-Text (Server-side)
```python
from correspondence.correspondence.utils.voice_to_text import VoiceToTextConverter, VoiceLetterCreator

# Convert audio
converter = VoiceToTextConverter()
text = converter.convert_audio_to_text('/path/to/audio.wav', 'en-US')

# Create letter from voice
creator = VoiceLetterCreator()
result = creator.create_letter_from_voice(
    '/path/to/audio.wav',
    'Incoming Letter',
    'en-US',
    {'department': 'Sales', 'priority': 'High'}
)
```

---

## Custom Script Examples

### Add Sign Button to Letter Form
```javascript
frappe.ui.form.on('Incoming Letter', {
  refresh: function(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__('Sign Document'), function() {
        frappe.call({
          method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
          args: {
            doctype: frm.doctype,
            docname: frm.docname
          },
          callback: function(r) {
            if (r.message.success) {
              frappe.msgprint(__('Document signed successfully'));
              frm.reload_doc();
            }
          }
        });
      }, __('Actions'));
    }
  }
});
```

### Add QR Code Button
```javascript
frappe.ui.form.on('Incoming Letter', {
  refresh: function(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__('Generate QR Code'), function() {
        frappe.call({
          method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
          args: {
            doctype: frm.doctype,
            docname: frm.docname,
            include_metadata: 1
          },
          callback: function(r) {
            if (r.message.success) {
              let html = `<img src="data:image/png;base64,${r.message.qr_image}" style="max-width: 300px;" />`;
              frappe.msgprint({
                title: __('QR Code'),
                message: html,
                wide: true
              });
            }
          }
        });
      }, __('Actions'));
    }
  }
});
```

### Show Analytics Dashboard
```javascript
frappe.ui.form.on('Incoming Letter', {
  refresh: function(frm) {
    frm.add_custom_button(__('Analytics'), function() {
      frappe.call({
        method: 'correspondence.correspondence.utils.ml_analytics.get_analytics_dashboard',
        args: { doctype: frm.doctype },
        callback: function(r) {
          // Display analytics in a dialog
          let d = new frappe.ui.Dialog({
            title: 'Analytics Dashboard',
            fields: [
              {
                fieldtype: 'HTML',
                fieldname: 'analytics_html'
              }
            ]
          });
          
          let html = `
            <h4>Trends</h4>
            <p>Total: ${r.message.trends.trends.total_letters}</p>
            <p>Daily Average: ${r.message.trends.trends.daily_average}</p>
            
            <h4>Insights</h4>
            ${r.message.insights.insights.map(i => `<p>[${i.severity}] ${i.message}</p>`).join('')}
          `;
          
          d.fields_dict.analytics_html.$wrapper.html(html);
          d.show();
        }
      });
    }, __('View'));
  }
});
```

---

## Common Patterns

### Background Job for Voice Processing
```python
frappe.enqueue(
    'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
    file_url=file_url,
    language='en-US',
    queue='long',
    timeout=600
)
```

### Caching Analytics Results
```python
cache_key = f'analytics_{doctype}_{period_days}'
cached = frappe.cache().get_value(cache_key)

if not cached:
    analytics = CorrespondenceAnalytics()
    result = analytics.analyze_trends(doctype, period_days)
    frappe.cache().set_value(cache_key, result, expires_in_sec=3600)
else:
    result = cached
```

### Error Handling
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
  args: { doctype: 'Incoming Letter', docname: 'INC-001' },
  callback: function(r) {
    if (r.message && r.message.success) {
      frappe.msgprint(__('Success'));
    } else {
      frappe.msgprint({
        title: __('Error'),
        message: r.message ? r.message.message : __('An error occurred'),
        indicator: 'red'
      });
    }
  },
  error: function(r) {
    frappe.msgprint({
      title: __('Error'),
      message: __('Failed to sign document'),
      indicator: 'red'
    });
  }
});
```

---

## Performance Tips

1. **Digital Signatures:** Cache user keys after generation
2. **QR Codes:** Store generated codes, don't regenerate
3. **Analytics:** Use background jobs for large datasets
4. **Voice:** Process long audio files in chunks
5. **General:** Use Redis caching for frequently accessed data

---

## Troubleshooting

### Check if module is loaded
```python
import frappe
frappe.get_module('correspondence.correspondence.utils.digital_signature')
```

### Test API endpoint
```bash
curl -X POST http://localhost:8000/api/method/correspondence.correspondence.utils.digital_signature.generate_user_keys \
  -H "Authorization: token YOUR_API_KEY:YOUR_API_SECRET"
```

### View error logs
```bash
tail -f sites/[site]/logs/frappe.log
```

---

**Version:** 1.0.1  
**Last Updated:** 2025-12-02
