"""
Tests for Event Database - Total Health Conferencing
Tests event CRUD operations and CSV import/export
"""
import pytest
from pathlib import Path
import tempfile
import sqlite3

from services.event_database import EventDatabase
from config.events import Event


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    db = EventDatabase(db_path)
    yield db

    # Cleanup
    db_path.unlink()


class TestEventDatabase:
    """Test event database operations"""

    def test_add_event(self, temp_db):
        """Test adding an event"""
        event_id = temp_db.add_event(
            meeting_name="Test Event 2025",
            meeting_date_long="May 1-3, 2025",
            venue="Test Venue",
            city_state="New York, NY",
            year=2025
        )

        assert event_id > 0

        # Verify it was added
        event = temp_db.get_event_by_id(event_id)
        assert event is not None
        assert event.meeting_name == "Test Event 2025"

    def test_add_duplicate_event(self, temp_db):
        """Test that duplicate event names are rejected"""
        temp_db.add_event(
            meeting_name="Unique Event",
            meeting_date_long="May 1-3, 2025",
            venue="Test Venue",
            city_state="New York, NY",
            year=2025
        )

        # Try to add duplicate
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.add_event(
                meeting_name="Unique Event",
                meeting_date_long="June 1-3, 2025",
                venue="Different Venue",
                city_state="Chicago, IL",
                year=2025
            )

    def test_get_all_events(self, temp_db):
        """Test retrieving all events"""
        # Add multiple events
        temp_db.add_event("Event 1", "May 1, 2025", "Venue 1", "NYC", 2025)
        temp_db.add_event("Event 2", "June 1, 2025", "Venue 2", "LA", 2025)
        temp_db.add_event("Event 3", "July 1, 2026", "Venue 3", "Chicago", 2026)

        all_events = temp_db.get_all_events()
        assert len(all_events) == 3

        # Filter by year
        events_2025 = temp_db.get_all_events(year=2025)
        assert len(events_2025) == 2

        events_2026 = temp_db.get_all_events(year=2026)
        assert len(events_2026) == 1

    def test_search_events(self, temp_db):
        """Test searching events by name"""
        temp_db.add_event("ASCO Direct 2025", "May 1, 2025", "Venue", "NYC", 2025)
        temp_db.add_event("Best of ASCO 2025", "June 1, 2025", "Venue", "LA", 2025)
        temp_db.add_event("Liver Meeting 2025", "July 1, 2025", "Venue", "CHI", 2025)

        # Search for ASCO
        results = temp_db.search_events("ASCO")
        assert len(results) == 2

        # Search for Best
        results = temp_db.search_events("Best")
        assert len(results) == 1

    def test_update_event(self, temp_db):
        """Test updating an event"""
        event_id = temp_db.add_event(
            "Original Name",
            "May 1, 2025",
            "Original Venue",
            "NYC",
            2025
        )

        # Update the event
        success = temp_db.update_event(
            event_id,
            "Updated Name",
            "June 1, 2025",
            "Updated Venue",
            "LA",
            2025
        )

        assert success

        # Verify update
        event = temp_db.get_event_by_id(event_id)
        assert event.meeting_name == "Updated Name"
        assert event.venue == "Updated Venue"

    def test_delete_event(self, temp_db):
        """Test deleting an event"""
        event_id = temp_db.add_event(
            "Event to Delete",
            "May 1, 2025",
            "Venue",
            "NYC",
            2025
        )

        # Delete the event
        success = temp_db.delete_event(event_id)
        assert success

        # Verify deletion
        event = temp_db.get_event_by_id(event_id)
        assert event is None

    def test_count_events(self, temp_db):
        """Test counting events"""
        assert temp_db.count_events() == 0

        temp_db.add_event("Event 1", "May 1, 2025", "Venue", "NYC", 2025)
        assert temp_db.count_events() == 1

        temp_db.add_event("Event 2", "June 1, 2025", "Venue", "LA", 2025)
        assert temp_db.count_events() == 2


class TestCSVOperations:
    """Test CSV import/export"""

    def test_export_to_csv(self, temp_db):
        """Test exporting events to CSV"""
        # Add events
        temp_db.add_event("Event 1", "May 1, 2025", "Venue 1", "NYC", 2025)
        temp_db.add_event("Event 2", "June 1, 2025", "Venue 2", "LA", 2025)

        # Export
        csv_buffer = temp_db.export_to_csv()

        assert csv_buffer is not None

        # Read back
        csv_buffer.seek(0)
        content = csv_buffer.read().decode('utf-8')

        assert 'Event 1' in content
        assert 'Event 2' in content
        assert 'Meeting Name' in content  # Header


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
