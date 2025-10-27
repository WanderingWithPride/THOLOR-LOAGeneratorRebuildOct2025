"""
Excel Bulk Processing - Total Health Conferencing
Handles Excel file parsing, event matching, and batch document generation
"""
import pandas as pd
from typing import List, Tuple, Optional, Dict
from io import BytesIO
import zipfile
from pathlib import Path

from core.models import ExcelRow, DocumentPayload
from services.event_matcher import EventMatcher, get_all_events
from generators.lor_generator import generate_lor_documents
from generators.loa_generator import generate_loa_documents
from config.pricing import calculate_pricing_for_event
from config.settings import DEFAULT_AUDIENCE


# ============================================================================
# EXCEL PARSING
# ============================================================================

class ExcelProcessor:
    """
    Processes Excel files for bulk document generation

    Handles:
    - Excel file parsing
    - Event name matching
    - Data validation
    - Batch document generation
    """

    # Expected column names (flexible matching)
    COLUMN_MAPPINGS = {
        # Required columns
        'exhibitor_invite': ['exhibitor invite', 'company', 'company name', 'exhibitor'],
        'event_name': ['event name', 'event', 'meeting name', 'meeting'],
        'total': ['total', 'amount', 'total amount', 'price'],

        # Optional columns
        'expected_attendance': ['expected attendance', 'attendance', 'attendees'],
        'date': ['date', 'meeting date', 'event date'],
        'city': ['city', 'location'],
        'venue': ['venue', 'location'],
        'official_address': ['official address', 'address', 'company address'],
        'amount': ['amount', 'booth amount'],
        'discount': ['discount'],
    }

    @staticmethod
    def parse_excel_file(file_obj) -> Tuple[List[ExcelRow], List[str]]:
        """
        Parse Excel file into ExcelRow objects

        Args:
            file_obj: Streamlit uploaded file object

        Returns:
            Tuple of (rows, errors)
        """
        errors = []
        rows = []

        try:
            # Read Excel file
            df = pd.read_excel(file_obj, engine='openpyxl')

            # Normalize column names (lowercase, strip whitespace)
            df.columns = df.columns.str.lower().str.strip()

            # Map columns to expected names
            column_map = ExcelProcessor._build_column_map(df.columns)

            # Check for required columns
            required = ['exhibitor_invite', 'event_name', 'total']
            missing = [col for col in required if col not in column_map]

            if missing:
                errors.append(f"Missing required columns: {', '.join(missing)}")
                return rows, errors

            # Process each row
            for idx, row in df.iterrows():
                try:
                    excel_row = ExcelProcessor._parse_row(row, column_map, idx + 2)  # +2 for Excel row number
                    rows.append(excel_row)
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")

            return rows, errors

        except Exception as e:
            errors.append(f"Failed to read Excel file: {str(e)}")
            return rows, errors

    @staticmethod
    def _build_column_map(columns: pd.Index) -> Dict[str, str]:
        """Build mapping from Excel columns to expected field names"""
        column_map = {}

        for field, variations in ExcelProcessor.COLUMN_MAPPINGS.items():
            for col in columns:
                if col in variations:
                    column_map[field] = col
                    break

        return column_map

    @staticmethod
    def _parse_row(row: pd.Series, column_map: Dict[str, str], row_number: int) -> ExcelRow:
        """Parse a single Excel row into ExcelRow object"""

        def get_value(field: str, default=None):
            """Safely get value from row"""
            col = column_map.get(field)
            if col is None:
                return default
            val = row.get(col)
            if pd.isna(val):
                return default
            return str(val).strip() if not isinstance(val, (int, float)) else val

        # Extract required fields
        exhibitor = get_value('exhibitor_invite', '')
        event = get_value('event_name', '')
        total = get_value('total', '0')

        # Extract optional fields
        excel_row = ExcelRow(
            exhibitor_invite=exhibitor,
            event_name=event,
            total=str(total),
            company_name=get_value('exhibitor_invite'),  # Same as exhibitor
            expected_attendance=get_value('expected_attendance'),
            date=get_value('date'),
            city=get_value('city'),
            venue=get_value('venue'),
            official_address=get_value('official_address'),
            amount=get_value('amount'),
            discount=get_value('discount'),
            row_number=row_number,
        )

        # Validate
        if not exhibitor:
            excel_row.add_error("Missing company name")
        if not event:
            excel_row.add_error("Missing event name")
        if not total or total == '0':
            excel_row.add_error("Missing or invalid total")

        return excel_row

    @staticmethod
    def match_events(rows: List[ExcelRow]) -> List[ExcelRow]:
        """
        Match Excel event names to system events

        Args:
            rows: List of ExcelRow objects

        Returns:
            Same list with matched_event field populated
        """
        all_events = get_all_events()

        for row in rows:
            if not row.event_name:
                row.add_error("No event name provided")
                continue

            # Try to match event
            matched = EventMatcher.find_best_match(row.event_name, all_events)

            if matched:
                row.matched_event = {
                    'meeting_name': matched.meeting_name,
                    'meeting_date_long': matched.meeting_date_long,
                    'venue': matched.venue,
                    'city_state': matched.city_state,
                    'event_year': matched.get_year(),
                }
            else:
                row.add_error(f"Could not match event: {row.event_name}")

        return rows

    @staticmethod
    def generate_batch_documents(
        rows: List[ExcelRow],
        document_type: str = "LOR",
        signatory_key: str = "sarah"
    ) -> Tuple[BytesIO, int, int]:
        """
        Generate documents for all valid rows and create ZIP file

        Args:
            rows: List of ExcelRow objects (with matched events)
            document_type: "LOR" or "LOA"
            signatory_key: Key for LOA signatory (sarah/michael/maureen)

        Returns:
            Tuple of (zip_buffer, success_count, error_count)
        """
        from config.settings import AUTHORIZED_SIGNATORIES

        # Create in-memory ZIP file
        zip_buffer = BytesIO()

        success_count = 0
        error_count = 0

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for row in rows:
                # Skip rows with errors
                if row.has_errors():
                    error_count += 1
                    continue

                if not row.matched_event:
                    error_count += 1
                    continue

                try:
                    # Build payload
                    signatory_info = AUTHORIZED_SIGNATORIES.get(signatory_key, AUTHORIZED_SIGNATORIES["sarah"])
                    signature_person = f"{signatory_info['name']} - {signatory_info['title']}"

                    payload = DocumentPayload(
                        company_name=row.company_name or row.exhibitor_invite,
                        company_address=row.official_address or "",
                        meeting_name=row.matched_event['meeting_name'],
                        meeting_date_long=row.matched_event['meeting_date_long'],
                        venue=row.matched_event['venue'],
                        city_state=row.matched_event['city_state'],
                        final_total=row.get_total_amount(),
                        amount_currency=row.total,
                        document_type=document_type,
                        signature_person=signature_person if document_type == "LOA" else None,
                        attendance_expected=row.expected_attendance,
                        audience_list=DEFAULT_AUDIENCE,
                        event_year=row.matched_event.get('event_year', 2025),
                    )

                    # Generate documents
                    if document_type == "LOA":
                        docx_buffer, pdf_buffer = generate_loa_documents(
                            payload,
                            signatory_key=signatory_key
                        )
                    else:
                        docx_buffer, pdf_buffer = generate_lor_documents(payload)

                    # Add to ZIP with unique filenames
                    company_slug = row.company_name.replace(' ', '_').replace('/', '_')[:50]
                    event_slug = row.matched_event['meeting_name'][:30].replace(' ', '_').replace('/', '_')

                    base_name = f"{document_type}_{company_slug}_{event_slug}"

                    zipf.writestr(f"{base_name}.docx", docx_buffer.getvalue())
                    zipf.writestr(f"{base_name}.pdf", pdf_buffer.getvalue())

                    success_count += 1

                except Exception as e:
                    row.add_error(f"Generation failed: {str(e)}")
                    error_count += 1

        zip_buffer.seek(0)
        return zip_buffer, success_count, error_count


# ============================================================================
# TEMPLATE GENERATION
# ============================================================================

def create_excel_template() -> BytesIO:
    """
    Create an Excel template file for bulk uploads

    Returns:
        BytesIO object containing Excel template
    """
    # Create sample data
    data = {
        'Exhibitor Invite': [
            'Sample Company Inc.',
            'Another Corp',
            'Medical Devices LLC',
        ],
        'Event Name': [
            'ASCO Direct from Chicago 2025',
            'Best of ASCO Seattle 2025',
            'Liver Meeting Direct from San Diego',
        ],
        'Total': [
            '$5,000.00',
            '$7,500.00',
            '$10,000.00',
        ],
        'Official Address': [
            '123 Main St, Suite 100, New York, NY 10001',
            '456 Corporate Blvd, Chicago, IL 60601',
            '789 Medical Plaza, Boston, MA 02101',
        ],
        'Expected Attendance': [
            250,
            300,
            200,
        ],
    }

    df = pd.DataFrame(data)

    # Write to BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Letters')

    buffer.seek(0)
    return buffer


# ============================================================================
# VALIDATION REPORT
# ============================================================================

def generate_validation_report(rows: List[ExcelRow]) -> str:
    """
    Generate a text report of validation results

    Args:
        rows: List of ExcelRow objects

    Returns:
        Formatted validation report
    """
    report_lines = ["# Validation Report\n"]

    total_rows = len(rows)
    valid_rows = [r for r in rows if not r.has_errors()]
    error_rows = [r for r in rows if r.has_errors()]

    report_lines.append(f"**Total Rows**: {total_rows}")
    report_lines.append(f"**Valid Rows**: {len(valid_rows)}")
    report_lines.append(f"**Rows with Errors**: {len(error_rows)}\n")

    if error_rows:
        report_lines.append("## Errors\n")
        for row in error_rows:
            report_lines.append(f"**Row {row.row_number}**: {row.company_name or row.exhibitor_invite}")
            for error in row.errors:
                report_lines.append(f"  - {error}")
            report_lines.append("")

    if valid_rows:
        report_lines.append("## Valid Rows (Ready to Generate)\n")
        for row in valid_rows[:10]:  # Show first 10
            report_lines.append(f"- **{row.company_name}** → {row.matched_event['meeting_name'] if row.matched_event else 'No match'}")

        if len(valid_rows) > 10:
            report_lines.append(f"\n... and {len(valid_rows) - 10} more")

    return "\n".join(report_lines)
