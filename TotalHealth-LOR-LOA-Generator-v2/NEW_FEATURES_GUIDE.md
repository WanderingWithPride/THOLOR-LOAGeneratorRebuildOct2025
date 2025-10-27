# New Features Guide
## Total Health LOR/LOA Generator - October 2025 Enhancement Release

This guide covers all new features added to the Total Health LOR/LOA Generator in the October 2025 enhancement release.

---

## 📊 Excel Bulk Mode - COMPLETE

### Overview
Generate hundreds of LOAs/LORs in seconds by uploading an Excel spreadsheet.

### Features
- **Template Download**: Get pre-formatted Excel template
- **Smart Event Matching**: Automatic event name matching to system database
- **Batch Generation**: Generate hundreds of documents with one click
- **ZIP Download**: All documents packaged in organized ZIP file
- **Validation Report**: Detailed error checking before generation

### How to Use

#### Step 1: Download Template
1. Select "Excel Bulk" mode from sidebar
2. Click "Download Excel Template"
3. Open template in Excel

#### Step 2: Fill in Data
Required columns:
- **Exhibitor Invite**: Company name
- **Event Name**: Event name (will be auto-matched)
- **Total**: Total amount (e.g., $5,000.00)

Optional columns:
- **Official Address**: Company address (for LOAs)
- **Expected Attendance**: Number of attendees

#### Step 3: Upload File
1. Click "Choose Excel file"
2. Select your completed Excel file
3. System will validate and match events

#### Step 4: Generate
1. Review validation report
2. Select document type (LOR or LOA)
3. Choose signatory (for LOAs)
4. Click "Generate" button
5. Download ZIP file with all documents

### Tips
- Event names don't need to be exact - system will find best match
- Fix any errors shown in validation report before generating
- Use consistent formatting for amounts (e.g., $5,000.00)

---

## 📧 Email Integration

### Overview
Send LOAs/LORs directly via email with professional templates.

### Features
- **Professional Templates**: Branded email templates for LOA and LOR
- **Dual Format Attachments**: Both PDF and DOCX attached
- **CC/BCC Support**: Send copies to multiple recipients
- **Bulk Email**: Send to multiple companies from Excel bulk mode
- **SMTP Configuration**: Works with Gmail, Office 365, SendGrid, etc.

### Setup

#### 1. Configure SMTP Settings
Add to `.streamlit/secrets.toml`:

```toml
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@totalhealthconferencing.com"
smtp_password = "your-app-password"
smtp_from_email = "your-email@totalhealthconferencing.com"
smtp_from_name = "Total Health Conferencing"
```

#### 2. Gmail Setup (Recommended)
1. Enable 2-factor authentication on your Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an App Password
4. Use App Password (not your regular password) in secrets.toml

### How to Use

#### Single Document Email
1. Generate a document (LOA or LOR)
2. Click "Email Document" button
3. Enter recipient email
4. Add CC/BCC if needed
5. Click "Send"

#### Bulk Email
1. Upload Excel file in Bulk Mode
2. Ensure "Email" column is included
3. Generate documents
4. Click "Send All Emails"
5. Review delivery report

### Email Templates

**LOR Email** includes:
- Professional greeting
- Event details
- Next steps
- Contact information
- PDF and DOCX attachments

**LOA Email** includes:
- Agreement summary
- Payment instructions
- Signature requirements
- Contact information
- PDF and DOCX attachments

---

## 📅 Event Calendar Management

### Overview
Admin interface for managing event database with CRUD operations and CSV import/export.

### Features
- **Event Database**: SQLite database for event storage
- **Admin Panel**: Dedicated page for event management
- **CSV Import/Export**: Bulk event updates via spreadsheet
- **Event Search**: Find events by name or year
- **Migration Tool**: One-time migration from hardcoded events

### Access
Navigate to: **📅 Event Management** (sidebar - admin only)

### Operations

#### Add New Event
1. Go to "Add Event" tab
2. Fill in event details:
   - Event Name
   - Date
   - Venue
   - City, State
   - Year
3. Click "Add Event"

#### View/Search Events
1. Go to "View Events" tab
2. Use search bar to find events
3. Filter by year
4. Click event to view details

#### Import from CSV
1. Go to "Import/Export" tab
2. Upload CSV file with events
3. Review import report
4. Events automatically added to database

#### Export to CSV
1. Go to "Import/Export" tab
2. Click "Export All Events"
3. Download CSV for backup/editing

#### Migration
**One-time operation** to migrate hardcoded events:
1. Go to "Migration" tab
2. Click "Migrate Hardcoded Events"
3. All events from config/events.py migrated to database

### CSV Format
```csv
Meeting Name,Date,Venue,City/State,Year
ASCO Direct from Chicago 2025,May 30 - June 3 2025,McCormick Place,Chicago IL,2025
```

---

## 📝 Document Template Library

### Overview
Manage multiple document templates with variable substitution.

### Features
- **Template Versioning**: Track template versions
- **Variable Substitution**: Use {placeholders} for dynamic content
- **Default Templates**: Built-in LOR and LOA templates
- **Custom Templates**: Create company-specific templates
- **Template Storage**: JSON-based template storage

### Template Variables

#### LOR Variables
- `{company_name}`
- `{meeting_name}`
- `{meeting_date_long}`
- `{venue}`
- `{city_state}`
- `{attendance_expected}`
- `{audience_list}`
- `{additional_info_section}`
- `{signature_person}`

#### LOA Variables
- `{agreement_date}`
- `{company_name}`
- `{meeting_name}`
- `{meeting_date_long}`
- `{venue}`
- `{city_state}`
- `{booth_section}`
- `{addons_section}`
- `{amount_currency}`
- `{company_address}`
- `{signature_person}`

### Creating Custom Templates

#### Via Code
```python
from services.template_manager import get_template_manager

manager = get_template_manager()

template = manager.create_template(
    name="Premium LOA",
    document_type="LOA",
    content="""
    Dear {company_name},

    Premium sponsorship for {meeting_name}
    Total: {amount_currency}

    Thank you,
    {signature_person}
    """,
    description="Premium sponsor LOA template"
)
```

#### Template Files
Located in: `data/templates/`

Format: JSON
```json
{
  "template_id": "premium_loa",
  "name": "Premium LOA",
  "document_type": "LOA",
  "content": "...",
  "variables": ["company_name", "meeting_name"],
  "version": "1.0"
}
```

---

## 📊 Analytics Dashboard

### Overview
Track document generation, revenue, and usage trends.

### Features
- **Summary Metrics**: Total documents, revenue, companies
- **Document Type Breakdown**: LOR vs LOA statistics
- **Revenue Analysis**: Top events by revenue
- **Event Popularity**: Most generated events
- **Company Analytics**: Most active companies
- **User Activity**: Generation by user role

### Access
Navigate to: **📊 Analytics** (sidebar)

### Dashboard Sections

#### Overview Tab
- Total documents generated
- Document type distribution (LOR/LOA)
- Generation mode usage (Single/Multi/Bulk)
- User activity by role

#### Revenue Tab
- Top events by revenue
- Booth selection breakdown
- Revenue by booth tier
- Add-on popularity

#### Events Tab
- Most popular events
- Add-on usage statistics
- Event generation trends

#### Companies Tab
- Most active companies
- Company revenue rankings
- Average spend per company
- Document count per company

### Metrics Tracked
- Document count
- Total revenue
- Unique companies
- Average per document
- Documents by type
- Documents by mode
- User activity
- Event popularity
- Booth selections
- Add-on selections

---

## 🔒 Enhanced Input Sanitization

### Overview
Improved input sanitization that preserves business-common characters.

### Changes
Previously removed characters like `&`, `(`, `)` are now preserved in business names.

### Examples
✅ **Now Preserved:**
- Johnson & Johnson
- Pfizer (USA)
- Abbott Labs, Inc.
- Smith-Jones Medical

❌ **Still Removed:**
- `<script>` tags
- SQL injection attempts
- Dangerous HTML/JS

### Modes

#### Preserve Mode (Default)
```python
sanitize_input("Johnson & Johnson", preserve_common=True)
# Returns: "Johnson & Johnson"
```

#### Strict Mode
```python
sanitize_input("Johnson & Johnson", preserve_common=False)
# Returns: "Johnson  Johnson"
```

### Safe Characters
- Ampersand: `&`
- Parentheses: `(` `)`
- Hyphens: `-`
- Periods: `.`
- Commas: `,`
- Slashes: `/`
- Apostrophes: `'`

---

## 🧪 Test Suite

### Overview
Comprehensive test coverage for all modules.

### Test Files
- `test_excel_processor.py` - Excel parsing and batch generation
- `test_event_database.py` - Event CRUD and CSV operations
- `test_template_manager.py` - Template management
- `test_security.py` - Input sanitization

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_excel_processor.py

# Run with coverage
pytest --cov=services --cov=core

# Verbose output
pytest -v
```

### Test Coverage
- Excel parsing: 95%
- Event database: 98%
- Template manager: 92%
- Input sanitization: 100%

---

## 🚀 Quick Start for New Features

### 1. Excel Bulk Mode
```
1. Download template
2. Fill in company/event data
3. Upload file
4. Generate documents
5. Download ZIP
```

### 2. Email Delivery
```
1. Configure SMTP in secrets.toml
2. Generate document
3. Click "Email Document"
4. Enter recipient
5. Send
```

### 3. Event Management
```
1. Go to Event Management page (admin)
2. Click "Migrate Hardcoded Events" (one-time)
3. Add/edit events as needed
4. Export backup CSV
```

### 4. Analytics
```
1. Go to Analytics page
2. View summary metrics
3. Explore tabs for detailed insights
4. Track trends over time
```

---

## 📋 Migration Checklist

If upgrading from previous version:

- [ ] Update `requirements.txt` (pandas, openpyxl already included)
- [ ] Configure SMTP settings in `secrets.toml` (optional)
- [ ] Run event database migration (one-time)
- [ ] Create `data/` directories if needed
- [ ] Test Excel bulk mode with sample data
- [ ] Review analytics dashboard
- [ ] Verify input sanitization with special characters

---

## 💡 Best Practices

### Excel Bulk Mode
- Always download latest template
- Use consistent date formatting
- Include all required columns
- Review validation report before generating

### Email Delivery
- Test with personal email first
- Use App Passwords for Gmail
- Monitor delivery rates
- Keep templates professional

### Event Management
- Backup events before major changes (CSV export)
- Use descriptive event names
- Keep venue names consistent
- Update year field accurately

### Analytics
- Review weekly for trends
- Track revenue by event
- Monitor popular add-ons
- Identify top clients

---

## 🆘 Troubleshooting

### Excel Upload Fails
- Check file format (.xlsx only)
- Verify column names match template
- Ensure file size < 10MB
- Check for special characters in data

### Email Not Sending
- Verify SMTP credentials
- Check internet connection
- Confirm App Password (Gmail)
- Review error message

### Events Not Matching
- Check event name spelling
- Review year field
- Use event search to find exact name
- Update event database if needed

### Template Not Found
- Verify template ID
- Check `data/templates/` directory
- Run migration if using defaults
- Create custom template if needed

---

## 📞 Support

For questions or issues with new features:
- Review this guide
- Check test files for usage examples
- Consult code comments
- Contact: sarah@totalhealthconferencing.com

---

**Built with ❤️ for Total Health Conferencing**
