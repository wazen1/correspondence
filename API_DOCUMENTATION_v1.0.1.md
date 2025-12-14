# API Documentation for Version 1.0.1 Features

This document provides detailed API documentation for the new features added in version 1.0.1.

## Table of Contents

1. [Digital Signature APIs](#digital-signature-apis)
2. [Barcode/QR Code APIs](#barcodeqr-code-apis)
3. [Advanced Analytics APIs](#advanced-analytics-apis)
4. [Voice-to-Text APIs](#voice-to-text-apis)

---

## Digital Signature APIs

### 1. Generate User Keys

Generate RSA key pair for the current user.

**Endpoint:** `/api/method/correspondence.correspondence.utils.digital_signature.generate_user_keys`

**Method:** POST

**Authentication:** Required

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Keys generated successfully",
  "public_key": "-----BEGIN PUBLIC KEY-----\n..."
}
```

**Example:**
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.generate_user_keys',
  callback: function(r) {
    console.log(r.message);
  }
});
```

---

### 2. Sign Document

Sign a document using the user's private key.

**Endpoint:** `/api/method/correspondence.correspondence.utils.digital_signature.sign_document_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type (e.g., "Incoming Letter")
- `docname` (string, required): Document name

**Response:**
```json
{
  "success": true,
  "message": "Document signed successfully",
  "signature": "base64_encoded_signature",
  "signer": "user@example.com",
  "timestamp": "2025-12-02T10:30:00"
}
```

**Example:**
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.digital_signature.sign_document_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001'
  },
  callback: function(r) {
    console.log(r.message);
  }
});
```

---

### 3. Verify Document Signature

Verify the signature of a document.

**Endpoint:** `/api/method/correspondence.correspondence.utils.digital_signature.verify_document_signature`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name
- `signer_email` (string, optional): Email of signer (defaults to current user)

**Response:**
```json
{
  "success": true,
  "is_valid": true,
  "signer": "user@example.com",
  "signature_date": "2025-12-02 10:30:00",
  "message": "Signature is valid"
}
```

---

### 4. Get Document Signatures

Get all signatures for a document.

**Endpoint:** `/api/method/correspondence.correspondence.utils.digital_signature.get_document_signatures`

**Method:** GET

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name

**Response:**
```json
[
  {
    "signer": "user1@example.com",
    "signature_date": "2025-12-02 10:30:00",
    "document_hash": "sha256_hash"
  },
  {
    "signer": "user2@example.com",
    "signature_date": "2025-12-02 11:00:00",
    "document_hash": "sha256_hash"
  }
]
```

---

## Barcode/QR Code APIs

### 1. Generate QR Code

Generate a QR code for a document.

**Endpoint:** `/api/method/correspondence.correspondence.utils.barcode_qr.generate_qr_code_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name
- `include_metadata` (int, optional): Include metadata (1 or 0, default: 1)

**Response:**
```json
{
  "success": true,
  "message": "QR code generated successfully",
  "qr_image": "base64_encoded_image",
  "doctype": "Incoming Letter",
  "docname": "INC-2025-00001"
}
```

**Example:**
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.barcode_qr.generate_qr_code_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001',
    include_metadata: 1
  },
  callback: function(r) {
    // Display QR code
    let img = '<img src="data:image/png;base64,' + r.message.qr_image + '" />';
    frappe.msgprint(img);
  }
});
```

---

### 2. Generate Barcode

Generate a barcode for a document.

**Endpoint:** `/api/method/correspondence.correspondence.utils.barcode_qr.generate_barcode_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name
- `barcode_type` (string, optional): Barcode type (default: 'code128')

**Response:**
```json
{
  "success": true,
  "message": "Barcode generated successfully",
  "barcode_image": "base64_encoded_image",
  "doctype": "Incoming Letter",
  "docname": "INC-2025-00001"
}
```

---

### 3. Get QR Code

Retrieve existing QR code for a document.

**Endpoint:** `/api/method/correspondence.correspondence.utils.barcode_qr.get_qr_code`

**Method:** GET

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name

**Response:**
```json
{
  "success": true,
  "qr_image": "base64_encoded_image",
  "qr_data": "{\"doctype\":\"Incoming Letter\",\"name\":\"INC-2025-00001\"}",
  "generated_date": "2025-12-02 10:30:00"
}
```

---

### 4. Scan QR Code

Process scanned QR code data.

**Endpoint:** `/api/method/correspondence.correspondence.utils.barcode_qr.scan_qr_code`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `qr_data` (string, required): JSON string from QR code

**Response:**
```json
{
  "success": true,
  "message": "Document found",
  "document": {
    "doctype": "Incoming Letter",
    "name": "INC-2025-00001",
    "url": "/app/incoming-letter/INC-2025-00001"
  }
}
```

---

## Advanced Analytics APIs

### 1. Predict Response Time

Predict expected response time for a letter using ML.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.predict_response_time_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name

**Response:**
```json
{
  "success": true,
  "predicted_response_days": 3.5,
  "expected_response_date": "2025-12-05",
  "confidence": "high"
}
```

**Example:**
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.ml_analytics.predict_response_time_api',
  args: {
    doctype: 'Incoming Letter',
    docname: 'INC-2025-00001'
  },
  callback: function(r) {
    if (r.message.success) {
      frappe.msgprint('Expected response in ' + r.message.predicted_response_days + ' days');
    }
  }
});
```

---

### 2. Predict Priority

Predict priority level for a letter based on content and metadata.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.predict_priority_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `docname` (string, required): Document name

**Response:**
```json
{
  "success": true,
  "predicted_priority": "High",
  "confidence": 85.5,
  "probabilities": {
    "Low": 5.2,
    "Medium": 9.3,
    "High": 85.5,
    "Urgent": 0.0
  }
}
```

---

### 3. Analyze Trends

Analyze correspondence trends over time.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.analyze_trends_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type
- `period_days` (int, optional): Number of days to analyze (default: 90)

**Response:**
```json
{
  "success": true,
  "period_days": 90,
  "trends": {
    "total_letters": 150,
    "daily_average": 1.67,
    "by_status": {
      "Completed": 80,
      "Pending": 50,
      "In Progress": 20
    },
    "by_priority": {
      "High": 60,
      "Medium": 70,
      "Low": 20
    },
    "weekly_trend": {
      "1": 15,
      "2": 18,
      "3": 20
    },
    "growth_rate": 12.5
  }
}
```

---

### 4. Identify Bottlenecks

Identify bottlenecks in correspondence processing.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.identify_bottlenecks_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type

**Response:**
```json
{
  "success": true,
  "total_pending": 50,
  "bottlenecks": [
    {
      "type": "department",
      "name": "Legal Department",
      "pending_count": 25,
      "severity": "high"
    },
    {
      "type": "aging",
      "name": "Old pending letters",
      "count": 15,
      "severity": "high"
    }
  ]
}
```

---

### 5. Generate Insights

Generate intelligent insights about correspondence.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.generate_insights_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type

**Response:**
```json
{
  "success": true,
  "insights": [
    {
      "type": "trend",
      "severity": "high",
      "message": "Letter volume has increased by 35%"
    },
    {
      "type": "alert",
      "severity": "high",
      "message": "45% of recent letters are high priority"
    }
  ],
  "summary": {
    "total_recent": 100,
    "completion_rate": 75.5,
    "high_priority_count": 45
  }
}
```

---

### 6. Get Analytics Dashboard

Get comprehensive analytics dashboard data.

**Endpoint:** `/api/method/correspondence.correspondence.utils.ml_analytics.get_analytics_dashboard`

**Method:** GET

**Authentication:** Required

**Parameters:**
- `doctype` (string, required): Document type

**Response:**
```json
{
  "trends": { ... },
  "bottlenecks": { ... },
  "insights": { ... }
}
```

---

## Voice-to-Text APIs

### 1. Convert Audio to Text

Convert an audio file to text.

**Endpoint:** `/api/method/correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `file_url` (string, required): URL of audio file
- `language` (string, optional): Language code (default: 'en-US')

**Response:**
```json
{
  "success": true,
  "message": "Audio converted successfully",
  "text": "This is the transcribed text from the audio recording",
  "language": "en-US"
}
```

**Example:**
```javascript
frappe.call({
  method: 'correspondence.correspondence.utils.voice_to_text.convert_audio_to_text_api',
  args: {
    file_url: '/files/recording.wav',
    language: 'en-US'
  },
  callback: function(r) {
    if (r.message.success) {
      console.log('Transcribed text:', r.message.text);
    }
  }
});
```

---

### 2. Create Letter from Voice

Create a letter document from a voice recording.

**Endpoint:** `/api/method/correspondence.correspondence.utils.voice_to_text.create_letter_from_voice_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `file_url` (string, required): URL of audio file
- `doctype` (string, required): Type of letter (e.g., "Incoming Letter")
- `language` (string, optional): Language code (default: 'en-US')
- `metadata` (string, optional): Additional metadata as JSON string

**Response:**
```json
{
  "success": true,
  "message": "Letter created successfully from voice recording",
  "letter_name": "INC-2025-00001",
  "subject": "This is the subject extracted from voice",
  "transcribed_text": "Full transcribed text..."
}
```

**Example:**
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
  callback: function(r) {
    if (r.message.success) {
      frappe.set_route('Form', 'Incoming Letter', r.message.letter_name);
    }
  }
});
```

---

### 3. Transcribe with Timestamps

Transcribe audio with word-level timestamps.

**Endpoint:** `/api/method/correspondence.correspondence.utils.voice_to_text.transcribe_with_timestamps_api`

**Method:** POST

**Authentication:** Required

**Parameters:**
- `file_url` (string, required): URL of audio file
- `language` (string, optional): Language code (default: 'en-US')

**Response:**
```json
{
  "success": true,
  "message": "Audio transcribed successfully",
  "timestamps": [
    {
      "word": "Hello",
      "start_time": 0.0,
      "end_time": 0.5
    },
    {
      "word": "world",
      "start_time": 0.5,
      "end_time": 1.0
    }
  ],
  "language": "en-US"
}
```

---

### 4. Get Supported Languages

Get list of supported languages for voice recognition.

**Endpoint:** `/api/method/correspondence.correspondence.utils.voice_to_text.get_supported_languages`

**Method:** GET

**Authentication:** Required

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "languages": {
    "en-US": "English (US)",
    "en-GB": "English (UK)",
    "ar-SA": "Arabic (Saudi Arabia)",
    "ar-EG": "Arabic (Egypt)",
    "fr-FR": "French",
    "de-DE": "German",
    "es-ES": "Spanish"
  }
}
```

---

## Error Handling

All APIs follow a consistent error response format:

```json
{
  "success": false,
  "message": "Error description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

API calls are subject to Frappe's standard rate limiting:
- 100 requests per minute per user
- 1000 requests per hour per user

---

## Best Practices

1. **Digital Signatures**: Always verify signatures before trusting document authenticity
2. **QR Codes**: Include metadata for better tracking and retrieval
3. **Analytics**: Use appropriate time periods for trend analysis (30-90 days recommended)
4. **Voice-to-Text**: Use high-quality audio recordings for better accuracy
5. **Error Handling**: Always check the `success` field in responses

---

## Support

For issues or questions about these APIs:
- GitHub Issues: [Create an issue]
- Email: admin@example.com
- Documentation: See README.md

---

**Version:** 1.0.1  
**Last Updated:** 2025-12-02
