# Correspondence - Archiving & Correspondence Management System

A complete, production-grade Archiving & Correspondence Management System for ERPNext v15, inspired by M-Files, SharePoint, and Alfresco.

## 🎯 Features

### Core Functionality
- ✅ **Incoming & Outgoing Letters** - Complete letter management with full tracking
- ✅ **Version Control** - Preserve original files, manage working copies (like M-Files)
- ✅ **OCR Integration** - Automatic text extraction from PDFs and images
- ✅ **AI-Powered Similarity Search** - Find related documents automatically using embeddings
- ✅ **Auto-Categorization** - Intelligent topic classification based on content
- ✅ **Full Archival System** - Physical and digital archive management
- ✅ **Workflow Automation** - Status tracking, SLA management, email notifications
- ✅ **Document Preview** - In-app PDF preview with PDF.js
- ✅ **Bulk Operations** - Import, archive, and process multiple documents

### Advanced Features
- 📊 **Dashboards** - Kanban, Calendar, Timeline, and List views
- 🔍 **Full-Text Search** - Search across OCR text, subjects, and metadata
- 📝 **Version History** - Complete audit trail with file comparison
- 🏷️ **Topic Management** - Hierarchical categorization with auto-rules
- 📍 **Archive Locations** - Physical location tracking (building/floor/shelf/box)
- 🔐 **Role-Based Permissions** - Granular access control
- 📧 **Email Integration** - Automatic notifications and assignments
- 📈 **Analytics** - Letter volume, response times, SLA compliance

## 📋 Requirements

### System Requirements
- ERPNext v15
- Python 3.10+
- Node.js 18+
- Tesseract OCR
- Poppler utilities

### Python Dependencies
```
pytesseract>=0.3.10
pdf2image>=1.16.3
Pillow>=10.0.0
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
scikit-learn>=1.3.0
numpy>=1.24.0
python-magic>=0.4.27
cryptography>=41.0.0
qrcode>=7.4.2
python-barcode>=0.15.1
pandas>=2.0.0
SpeechRecognition>=3.10.0
pydub>=0.25.1
```

### Node Dependencies
```
pdfjs-dist@^3.11.174
```

## 🚀 Installation

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng

# Install Poppler (for PDF processing)
sudo apt-get install -y poppler-utils

# Verify installation
tesseract --version
```

**CentOS/RHEL:**
```bash
sudo yum install -y tesseract poppler-utils
```

### Step 2: Install the App

```bash
# Navigate to your bench directory
cd /home/erp/frappe-bench

# The app is already created, now install it on your site
bench --site [your-site-name] install-app correspondence

# Install Python dependencies
cd apps/correspondence
pip install -r requirements.txt

# Install Node dependencies
npm install

# Build assets
cd ../..
bench build --app correspondence
```

### Step 3: Run Migrations

```bash
bench --site [your-site-name] migrate
```

### Step 4: Setup Permissions

```bash
# Create custom roles (via ERPNext UI or console)
bench --site [your-site-name] console
```

In the console:
```python
# Create Correspondence Manager role
if not frappe.db.exists("Role", "Correspondence Manager"):
    role = frappe.new_doc("Role")
    role.role_name = "Correspondence Manager"
    role.desk_access = 1
    role.insert()

# Create Correspondence User role
if not frappe.db.exists("Role", "Correspondence User"):
    role = frappe.new_doc("Role")
    role.role_name = "Correspondence User"
    role.desk_access = 1
    role.insert()

frappe.db.commit()
```

### Step 5: Restart Services

```bash
bench restart
```

## 📚 Usage Guide

### Creating an Incoming Letter

1. Navigate to **Correspondence > Incoming Letter > New**
2. Fill in the required fields:
   - Sender
   - Recipient Department
   - Subject
   - Date Received
   - Priority
3. Upload attachments (PDF/images)
4. OCR will automatically extract text
5. Related documents will be suggested automatically
6. Topics will be auto-assigned based on content
7. Save and Submit

### Creating an Outgoing Letter

1. Navigate to **Correspondence > Outgoing Letter > New**
2. Fill in:
   - Recipient
   - Department
   - Subject
   - Body Text
3. Optionally link to an incoming letter
4. Upload attachments
5. Save as Draft or Submit

### Version Control Workflow

1. **Original File**: First attachment is automatically locked as original
2. **Edit Document**: Click "Create Working Copy" button
3. **Modify**: Edit the working copy
4. **Save Version**: Upload modified file - new version is created
5. **Compare**: View version history and compare changes

### Archiving Documents

**Single Document:**
1. Open the letter
2. Change status to "Archived"
3. Archive number is auto-generated
4. Document becomes read-only

**Bulk Archive:**
1. Select multiple letters from list view
2. Click "Actions" > "Bulk Archive"
3. All selected documents are archived

### Setting Up Topics

1. Navigate to **Correspondence > Topic > New**
2. Enter Topic Name
3. Add Keywords (comma-separated)
4. Optionally add Advanced Rules (JSON)
5. Enable Auto Categorization
6. Save

**Example Advanced Rule:**
```json
{
  "operator": "OR",
  "conditions": [
    {"field": "text", "operator": "contains", "value": "contract"},
    {"field": "text", "operator": "contains", "value": "agreement"}
  ]
}
```

## 🏗️ Architecture

### Doctypes

1. **Incoming Letter** - Incoming correspondence
2. **Outgoing Letter** - Outgoing correspondence
3. **Document Version** - Version control records
4. **Topic** - Categories/topics for classification
5. **Letter Attachment** (Child) - File attachments with OCR
6. **Related Document** (Child) - Linked documents
7. **Archive Location** - Physical archive locations

### Modules Structure

```
correspondence/
├── doctype/          # All doctypes
├── api/              # REST API endpoints
├── utils/            # Utility modules
│   ├── ocr_processor.py
│   ├── similarity_engine.py
│   ├── version_control.py
│   └── topic_classifier.py
├── page/             # Custom pages
└── public/           # Frontend assets
```

### API Endpoints

All endpoints are whitelisted and accessible via:
```
/api/method/correspondence.correspondence.utils.[module].[function]
```

**OCR APIs:**
- `process_file_ocr(file_url)` - Process OCR for a file
- `batch_process_ocr(file_urls)` - Batch OCR processing

**Similarity APIs:**
- `get_similar_documents(doctype, docname)` - Get related documents

**Version Control APIs:**
- `get_version_history_api(doctype, docname)` - Get version history
- `create_working_copy_api(doctype, docname)` - Create working copy
- `save_version_api(doctype, docname, file_url, changes_summary)` - Save new version

**Topic Classification APIs:**
- `classify_document_api(doctype, docname)` - Auto-classify document
- `apply_topics_to_document(doctype, docname, topics)` - Apply topics

**Archive APIs:**
- `bulk_archive(letter_names)` - Bulk archive letters

## 🔧 Configuration

### OCR Language Support

By default, OCR supports English and Arabic. To add more languages:

```bash
# List available languages
tesseract --list-langs

# Install additional language
sudo apt-get install tesseract-ocr-[lang-code]

# Update ocr_processor.py to include new language
# Change: lang='eng+ara'
# To: lang='eng+ara+fra' (for French)
```

### Similarity Search Tuning

Edit `similarity_engine.py` to adjust:
- **Model**: Change `paraphrase-multilingual-MiniLM-L12-v2` to other models
- **Threshold**: Adjust `threshold=0.3` (0-1 scale)
- **Limit**: Change `limit=10` for more/fewer results

### Workflow Customization

1. Navigate to **Workflow > New**
2. Select Document Type (Incoming Letter / Outgoing Letter)
3. Define States and Transitions
4. Set Email Alerts
5. Configure SLA

## 📊 Dashboards & Reports

### Available Views

1. **Kanban View** - Drag-and-drop status management
2. **Calendar View** - Date-based visualization
3. **List View** - Filterable table with search
4. **Timeline View** - Chronological display

### Standard Filters

- Department
- Status
- Priority
- Date Range
- Sender/Recipient
- Topics
- Has Attachments

### Creating Custom Reports

```python
# Example: Letters by Department
frappe.db.sql("""
    SELECT 
        department,
        COUNT(*) as total_letters,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
    FROM `tabIncoming Letter`
    GROUP BY department
""", as_dict=True)
```

## 🔐 Security & Permissions

### Role Hierarchy

1. **System Manager** - Full access
2. **Correspondence Manager** - Create, edit, delete, archive
3. **Correspondence User** - Create, edit, view

### Archived Documents

- Read-only for all users except System Manager
- Version history preserved
- Cannot be deleted
- Can be unarchived by System Manager only

## 🐛 Troubleshooting

### OCR Not Working

```bash
# Check Tesseract installation
tesseract --version

# Check Python dependencies
pip list | grep pytesseract

# Check logs
tail -f sites/[site]/logs/frappe.log
```

### Similarity Search Not Working

```bash
# Install sentence-transformers
pip install sentence-transformers

# Download model (first run may take time)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

### Performance Issues

- Enable Redis caching
- Index frequently queried fields
- Use background jobs for OCR processing
- Optimize similarity search threshold

## 📈 Performance Optimization

### Database Indexes

```sql
-- Add indexes for better performance
ALTER TABLE `tabIncoming Letter` ADD INDEX idx_status (status);
ALTER TABLE `tabIncoming Letter` ADD INDEX idx_department (department);
ALTER TABLE `tabIncoming Letter` ADD INDEX idx_date_received (date_received);
```

### Background Jobs

For large files, process OCR in background:

```python
frappe.enqueue(
    'correspondence.correspondence.utils.ocr_processor.process_file_ocr',
    file_url=file_url,
    queue='long'
)
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

MIT License

Copyright (c) 2025 ERP Team

## 🆘 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: admin@example.com
- Documentation: [Link to docs]

## 🗺️ Roadmap

### Completed in Version 1.0.1

- [x] Digital signature support
- [x] Barcode/QR code generation
- [x] Advanced analytics with ML
- [x] Voice-to-text for letter creation

### Planned Features

- [ ] Email integration (auto-create letters from emails)
- [ ] Mobile app
- [ ] Multi-language UI
- [ ] Integration with external DMS systems
- [ ] Automated workflow suggestions

## 📝 Changelog

### Version 1.0.1 (2025-12-02)

**New Features**
- ✅ Digital signature support with RSA encryption
  - Generate user key pairs
  - Sign documents digitally
  - Verify document signatures
  - Track signature history
- ✅ Barcode/QR code generation
  - Generate QR codes with document metadata
  - Generate barcodes for document tracking
  - Scan QR codes to retrieve documents
  - Multiple barcode format support
- ✅ Advanced analytics with ML
  - Predict response times using machine learning
  - Auto-classify priority levels
  - Trend analysis and forecasting
  - Bottleneck identification
  - Intelligent insights generation
- ✅ Voice-to-text for letter creation
  - Convert audio recordings to text
  - Create letters from voice recordings
  - Multi-language support
  - Automatic subject/body extraction

**Dependencies Added**
- cryptography>=41.0.0
- qrcode>=7.4.2
- python-barcode>=0.15.1
- pandas>=2.0.0
- SpeechRecognition>=3.10.0
- pydub>=0.25.1

### Version 1.0.0 (2025-11-25)

**Initial Release**
- Complete letter management system
- OCR integration
- Similarity search
- Version control
- Auto-categorization
- Archive management
- Workflows and notifications

---

**Built with ❤️ for ERPNext Community**
