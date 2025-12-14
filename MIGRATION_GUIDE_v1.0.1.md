# Migration Guide: Upgrading to Version 1.0.1

This guide will help you upgrade your Correspondence app from version 1.0.0 to version 1.0.1.

## Overview

Version 1.0.1 introduces four major new features:
1. Digital Signature Support
2. Barcode/QR Code Generation
3. Advanced Analytics with ML
4. Voice-to-Text for Letter Creation

## Prerequisites

- ERPNext v15
- Python 3.10+
- Frappe bench environment
- Backup of your current database

## Step-by-Step Upgrade Process

### Step 1: Backup Your Data

**IMPORTANT:** Always backup before upgrading!

```bash
# Navigate to your bench directory
cd /home/erp/frappe-bench

# Backup your site
bench --site [your-site-name] backup --with-files

# Backups are stored in: sites/[your-site-name]/private/backups/
```

### Step 2: Pull Latest Code

```bash
# Navigate to the app directory
cd apps/correspondence

# Pull latest changes (if using git)
git pull origin main

# Or if you're updating manually, ensure all new files are in place
```

### Step 3: Install New Python Dependencies

```bash
# Navigate to bench directory
cd /home/erp/frappe-bench

# Install new dependencies
pip install -r apps/correspondence/requirements.txt

# Verify installations
pip list | grep -E "cryptography|qrcode|barcode|pandas|SpeechRecognition|pydub"
```

**New dependencies installed:**
- `cryptography>=41.0.0` - For digital signatures
- `qrcode>=7.4.2` - For QR code generation
- `python-barcode>=0.15.1` - For barcode generation
- `pandas>=2.0.0` - For analytics
- `SpeechRecognition>=3.10.0` - For voice recognition
- `pydub>=0.25.1` - For audio processing

### Step 4: Install System Dependencies (for Voice-to-Text)

**Ubuntu/Debian:**
```bash
# Install FFmpeg (required by pydub)
sudo apt-get update
sudo apt-get install -y ffmpeg

# Verify installation
ffmpeg -version
```

**CentOS/RHEL:**
```bash
sudo yum install -y ffmpeg
```

### Step 5: Create New DocTypes

The following new DocTypes need to be created:

1. **Document Signature** - Stores digital signatures
2. **User Signature Keys** - Stores user key pairs
3. **Document QR Code** - Stores QR codes
4. **Document Barcode** - Stores barcodes

Create these DocTypes manually or use the provided JSON files:

```bash
# Navigate to bench directory
cd /home/erp/frappe-bench

# Run migrations to create new DocTypes
bench --site [your-site-name] migrate
```

### Step 6: Build Assets

```bash
# Build frontend assets
bench build --app correspondence

# Or for production
bench build --app correspondence --production
```

### Step 7: Restart Services

```bash
# Restart all services
bench restart

# Or restart specific services
sudo supervisorctl restart all
```

### Step 8: Verify Installation

```bash
# Open Frappe console
bench --site [your-site-name] console
```

In the console, verify the new modules are loaded:

```python
# Test digital signature module
from correspondence.correspondence.utils.digital_signature import DigitalSignatureManager
manager = DigitalSignatureManager()
print("Digital Signature: OK")

# Test barcode/QR module
from correspondence.correspondence.utils.barcode_qr import BarcodeQRGenerator
generator = BarcodeQRGenerator()
print("Barcode/QR: OK")

# Test analytics module
from correspondence.correspondence.utils.ml_analytics import CorrespondenceAnalytics
analytics = CorrespondenceAnalytics()
print("Analytics: OK")

# Test voice-to-text module
from correspondence.correspondence.utils.voice_to_text import VoiceToTextConverter
converter = VoiceToTextConverter()
print("Voice-to-Text: OK")

# Exit console
exit()
```

### Step 9: Set Up Permissions

Grant permissions for new features:

```bash
bench --site [your-site-name] console
```

```python
# Grant permissions for Document Signature
frappe.permissions.add_permission("Document Signature", "Correspondence Manager", 0)
frappe.permissions.add_permission("Document Signature", "Correspondence User", 0)

# Grant permissions for User Signature Keys
frappe.permissions.add_permission("User Signature Keys", "Correspondence Manager", 0)
frappe.permissions.add_permission("User Signature Keys", "All", 0, ptype="read")

# Grant permissions for Document QR Code
frappe.permissions.add_permission("Document QR Code", "Correspondence Manager", 0)
frappe.permissions.add_permission("Document QR Code", "Correspondence User", 0)

# Grant permissions for Document Barcode
frappe.permissions.add_permission("Document Barcode", "Correspondence Manager", 0)
frappe.permissions.add_permission("Document Barcode", "Correspondence User", 0)

frappe.db.commit()
exit()
```

## New DocType Structures

### Document Signature

```json
{
  "doctype": "Document Signature",
  "fields": [
    {"fieldname": "document_type", "fieldtype": "Link", "options": "DocType"},
    {"fieldname": "document_name", "fieldtype": "Data"},
    {"fieldname": "signature", "fieldtype": "Long Text"},
    {"fieldname": "signer", "fieldtype": "Link", "options": "User"},
    {"fieldname": "document_hash", "fieldtype": "Data"},
    {"fieldname": "signature_date", "fieldtype": "Datetime"}
  ]
}
```

### User Signature Keys

```json
{
  "doctype": "User Signature Keys",
  "fields": [
    {"fieldname": "user", "fieldtype": "Link", "options": "User"},
    {"fieldname": "private_key", "fieldtype": "Long Text"},
    {"fieldname": "public_key", "fieldtype": "Long Text"}
  ]
}
```

### Document QR Code

```json
{
  "doctype": "Document QR Code",
  "fields": [
    {"fieldname": "document_type", "fieldtype": "Link", "options": "DocType"},
    {"fieldname": "document_name", "fieldtype": "Data"},
    {"fieldname": "qr_image", "fieldtype": "Long Text"},
    {"fieldname": "qr_data", "fieldtype": "Long Text"},
    {"fieldname": "generated_date", "fieldtype": "Datetime"}
  ]
}
```

### Document Barcode

```json
{
  "doctype": "Document Barcode",
  "fields": [
    {"fieldname": "document_type", "fieldtype": "Link", "options": "DocType"},
    {"fieldname": "document_name", "fieldtype": "Data"},
    {"fieldname": "barcode_image", "fieldtype": "Long Text"},
    {"fieldname": "barcode_data", "fieldtype": "Data"},
    {"fieldname": "barcode_type", "fieldtype": "Data"},
    {"fieldname": "generated_date", "fieldtype": "Datetime"}
  ]
}
```

## Testing New Features

### Test Digital Signatures

```javascript
// In browser console or custom script
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.generate_user_keys',
  callback: function(r) {
    console.log('Keys generated:', r.message);
  }
});

frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001'
  },
  callback: function(r) {
    console.log('Document signed:', r.message);
  }
});
```

### Test QR Code Generation

```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001',
    include_metadata: 1
  },
  callback: function(r) {
    console.log('QR code generated:', r.message);
  }
});
```

### Test Analytics

```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.predict_response_time_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001'
  },
  callback: function(r) {
    console.log('Predicted response time:', r.message);
  }
});
```

### Test Voice-to-Text

```javascript
// First upload an audio file, then:
frappe.call({
  method: 'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
  args: {
    file_url: '/files/recording.wav',
    language: 'en-US'
  },
  callback: function(r) {
    console.log('Transcribed text:', r.message);
  }
});
```

## Troubleshooting

### Issue: Import errors for new modules

**Solution:**
```bash
# Reinstall dependencies
pip install -r apps/correspondence/requirements.txt --force-reinstall

# Restart bench
bench restart
```

### Issue: Digital signatures not working

**Solution:**
```bash
# Verify cryptography installation
python -c "from cryptography.hazmat.primitives.asymmetric import rsa; print('OK')"

# If error, reinstall
pip install cryptography --upgrade
```

### Issue: QR codes not generating

**Solution:**
```bash
# Verify qrcode and Pillow installation
python -c "import qrcode; print('OK')"

# If error, reinstall
pip install qrcode Pillow --upgrade
```

### Issue: Voice-to-text not working

**Solution:**
```bash
# Verify FFmpeg installation
ffmpeg -version

# Verify SpeechRecognition
python -c "import speech_recognition as sr; print('OK')"

# If error, reinstall system dependencies
sudo apt-get install -y ffmpeg
pip install SpeechRecognition pydub --upgrade
```

### Issue: Analytics predictions failing

**Solution:**
```bash
# Verify scikit-learn and pandas
python -c "import sklearn; import pandas; print('OK')"

# If error, reinstall
pip install scikit-learn pandas --upgrade
```

## Performance Considerations

### Digital Signatures
- Key generation is CPU-intensive; cache keys after generation
- Signature verification is fast but should be done asynchronously for bulk operations

### QR Codes
- QR code generation is lightweight
- Store generated QR codes to avoid regeneration

### Analytics
- ML predictions require historical data (minimum 20-50 records)
- Use background jobs for large dataset analysis
- Cache analytics results for frequently accessed data

### Voice-to-Text
- Audio processing is CPU and memory intensive
- Use background jobs for large audio files
- Recommended max file size: 10MB
- For longer recordings, use chunked processing

## Background Job Configuration

For better performance, configure background jobs:

```python
# In hooks.py or custom script
frappe.enqueue(
    'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
    file_url=file_url,
    language='en-US',
    queue='long',
    timeout=600
)
```

## Rollback Procedure

If you need to rollback to version 1.0.0:

```bash
# Restore from backup
bench --site [your-site-name] restore [backup-file]

# Checkout previous version (if using git)
cd apps/correspondence
git checkout v1.0.0

# Reinstall old dependencies
pip install -r requirements.txt

# Migrate
bench --site [your-site-name] migrate

# Restart
bench restart
```

## Post-Upgrade Checklist

- [ ] All dependencies installed successfully
- [ ] New DocTypes created
- [ ] Permissions configured
- [ ] Digital signatures working
- [ ] QR/Barcode generation working
- [ ] Analytics predictions working
- [ ] Voice-to-text conversion working
- [ ] All existing features still functional
- [ ] Performance is acceptable
- [ ] Error logs are clean

## Support

If you encounter issues during migration:

1. Check error logs: `tail -f sites/[site]/logs/frappe.log`
2. Review this migration guide
3. Check API documentation: `API_DOCUMENTATION_v1.0.1.md`
4. Contact support: admin@example.com
5. Create GitHub issue with error details

## Next Steps

After successful migration:

1. Train users on new features
2. Generate signature keys for all users
3. Set up analytics dashboards
4. Configure voice-to-text language preferences
5. Test QR code scanning workflow

---

**Version:** 1.0.1  
**Last Updated:** 2025-12-02  
**Estimated Migration Time:** 30-45 minutes
