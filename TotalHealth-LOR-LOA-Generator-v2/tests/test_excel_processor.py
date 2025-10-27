"""
Tests for Excel Processor - Total Health Conferencing
Tests Excel parsing, event matching, and batch generation
"""
import pytest
from io import BytesIO
import pandas as pd

from services.excel_processor import ExcelProcessor, create_excel_template
from core.models import ExcelRow


class TestExcelProcessor:
    """Test Excel file processing"""

    def test_create_template(self):
        """Test Excel template creation"""
        template = create_excel_template()

        assert template is not None
        assert isinstance(template, BytesIO)

        # Verify it's a valid Excel file
        template.seek(0)
        df = pd.read_excel(template, engine='openpyxl')

        assert len(df) == 3  # Sample data has 3 rows
        assert 'Exhibitor Invite' in df.columns
        assert 'Event Name' in df.columns
        assert 'Total' in df.columns

    def test_parse_row(self):
        """Test parsing a single Excel row"""
        # Create sample row
        row_data = {
            'exhibitor invite': 'Test Company',
            'event name': 'ASCO Direct 2025',
            'total': '$5,000.00',
            'official address': '123 Main St',
        }

        row = pd.Series(row_data)
        column_map = {
            'exhibitor_invite': 'exhibitor invite',
            'event_name': 'event name',
            'total': 'total',
            'official_address': 'official address',
        }

        excel_row = ExcelProcessor._parse_row(row, column_map, 2)

        assert excel_row.exhibitor_invite == 'Test Company'
        assert excel_row.event_name == 'ASCO Direct 2025'
        assert excel_row.total == '$5,000.00'
        assert excel_row.official_address == '123 Main St'
        assert not excel_row.has_errors()

    def test_parse_row_missing_fields(self):
        """Test parsing row with missing required fields"""
        row_data = {
            'exhibitor invite': '',
            'event name': 'ASCO Direct 2025',
            'total': '',
        }

        row = pd.Series(row_data)
        column_map = {
            'exhibitor_invite': 'exhibitor invite',
            'event_name': 'event name',
            'total': 'total',
        }

        excel_row = ExcelProcessor._parse_row(row, column_map, 2)

        assert excel_row.has_errors()
        assert len(excel_row.errors) >= 2  # Missing company and total

    def test_get_total_amount(self):
        """Test extracting numeric total from string"""
        row = ExcelRow(
            exhibitor_invite='Test',
            event_name='Test Event',
            total='$5,000.00'
        )

        assert row.get_total_amount() == 5000.0

        # Test different formats
        row.total = '$10,500.50'
        assert row.get_total_amount() == 10500.50

        row.total = '7500'
        assert row.get_total_amount() == 7500.0


class TestColumnMapping:
    """Test column name mapping"""

    def test_build_column_map(self):
        """Test building column map from Excel columns"""
        columns = pd.Index([
            'exhibitor invite',
            'event name',
            'total',
            'official address'
        ])

        column_map = ExcelProcessor._build_column_map(columns)

        assert 'exhibitor_invite' in column_map
        assert 'event_name' in column_map
        assert 'total' in column_map
        assert 'official_address' in column_map

    def test_column_variations(self):
        """Test that column variations are recognized"""
        # Test 'company' as variation of 'exhibitor_invite'
        columns = pd.Index(['company', 'event', 'total'])

        column_map = ExcelProcessor._build_column_map(columns)

        assert 'exhibitor_invite' in column_map
        assert column_map['exhibitor_invite'] == 'company'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
