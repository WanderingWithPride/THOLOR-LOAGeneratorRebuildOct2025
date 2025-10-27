"""
Event Database - Total Health Conferencing
SQLite database for event calendar management with CSV import/export
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import csv
from io import StringIO, BytesIO

from config.events import Event


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_PATH = Path(__file__).parent.parent / "data" / "events.db"


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_name TEXT NOT NULL UNIQUE,
    meeting_date_long TEXT NOT NULL,
    venue TEXT NOT NULL,
    city_state TEXT NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_year ON events(year);
CREATE INDEX IF NOT EXISTS idx_meeting_name ON events(meeting_name);
"""


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class EventDatabase:
    """
    Manages event storage in SQLite database

    Provides:
    - CRUD operations
    - CSV import/export
    - Event search and filtering
    - Migration from hardcoded events
    """

    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ========================================================================
    # CREATE
    # ========================================================================

    def add_event(
        self,
        meeting_name: str,
        meeting_date_long: str,
        venue: str,
        city_state: str,
        year: int
    ) -> int:
        """
        Add new event to database

        Args:
            meeting_name: Event name
            meeting_date_long: Full date string
            venue: Venue name
            city_state: City and state
            year: Event year

        Returns:
            Event ID

        Raises:
            sqlite3.IntegrityError: If event name already exists
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (meeting_name, meeting_date_long, venue, city_state, year)
                VALUES (?, ?, ?, ?, ?)
                """,
                (meeting_name, meeting_date_long, venue, city_state, year)
            )
            conn.commit()
            return cursor.lastrowid

    def add_event_from_object(self, event: Event) -> int:
        """Add event from Event object"""
        return self.add_event(
            meeting_name=event.meeting_name,
            meeting_date_long=event.meeting_date_long,
            venue=event.venue,
            city_state=event.city_state,
            year=event.get_year()
        )

    # ========================================================================
    # READ
    # ========================================================================

    def get_all_events(self, year: Optional[int] = None) -> List[Event]:
        """
        Get all events, optionally filtered by year

        Args:
            year: Filter by year (None = all years)

        Returns:
            List of Event objects
        """
        with self._get_connection() as conn:
            if year:
                cursor = conn.execute(
                    "SELECT * FROM events WHERE year = ? ORDER BY meeting_date_long",
                    (year,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM events ORDER BY year DESC, meeting_date_long"
                )

            rows = cursor.fetchall()

        return [self._row_to_event(row) for row in rows]

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()

        if row:
            return self._row_to_event(row)
        return None

    def get_event_by_name(self, meeting_name: str) -> Optional[Event]:
        """Get event by exact name match"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM events WHERE meeting_name = ?",
                (meeting_name,)
            )
            row = cursor.fetchone()

        if row:
            return self._row_to_event(row)
        return None

    def search_events(self, query: str) -> List[Event]:
        """
        Search events by name (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching Event objects
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM events
                WHERE meeting_name LIKE ?
                ORDER BY meeting_date_long
                """,
                (f"%{query}%",)
            )
            rows = cursor.fetchall()

        return [self._row_to_event(row) for row in rows]

    def get_years(self) -> List[int]:
        """Get list of all years with events"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT year FROM events ORDER BY year DESC")
            rows = cursor.fetchall()

        return [row['year'] for row in rows]

    def count_events(self) -> int:
        """Get total number of events"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM events")
            return cursor.fetchone()['count']

    # ========================================================================
    # UPDATE
    # ========================================================================

    def update_event(
        self,
        event_id: int,
        meeting_name: str,
        meeting_date_long: str,
        venue: str,
        city_state: str,
        year: int
    ) -> bool:
        """
        Update existing event

        Args:
            event_id: Event ID
            meeting_name: Event name
            meeting_date_long: Full date string
            venue: Venue name
            city_state: City and state
            year: Event year

        Returns:
            True if updated, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE events
                SET meeting_name = ?,
                    meeting_date_long = ?,
                    venue = ?,
                    city_state = ?,
                    year = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (meeting_name, meeting_date_long, venue, city_state, year, event_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ========================================================================
    # DELETE
    # ========================================================================

    def delete_event(self, event_id: int) -> bool:
        """
        Delete event by ID

        Args:
            event_id: Event ID

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0

    def delete_events_by_year(self, year: int) -> int:
        """
        Delete all events for a given year

        Args:
            year: Year to delete

        Returns:
            Number of events deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM events WHERE year = ?", (year,))
            conn.commit()
            return cursor.rowcount

    # ========================================================================
    # CSV IMPORT/EXPORT
    # ========================================================================

    def export_to_csv(self) -> BytesIO:
        """
        Export all events to CSV

        Returns:
            BytesIO buffer with CSV data
        """
        events = self.get_all_events()

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Meeting Name', 'Date', 'Venue', 'City/State', 'Year'])

        # Write data
        for event in events:
            writer.writerow([
                event.meeting_name,
                event.meeting_date_long,
                event.venue,
                event.city_state,
                event.get_year()
            ])

        # Convert to bytes
        csv_bytes = BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        return csv_bytes

    def import_from_csv(self, csv_file) -> tuple[int, int, List[str]]:
        """
        Import events from CSV file

        Args:
            csv_file: File object or BytesIO

        Returns:
            Tuple of (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        errors = []

        try:
            # Read CSV
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            reader = csv.DictReader(StringIO(content))

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    # Extract fields (case-insensitive)
                    row_lower = {k.lower().strip(): v for k, v in row.items()}

                    meeting_name = row_lower.get('meeting name', '').strip()
                    date = row_lower.get('date', '').strip()
                    venue = row_lower.get('venue', '').strip()
                    city_state = row_lower.get('city/state', row_lower.get('city', '')).strip()
                    year_str = row_lower.get('year', '').strip()

                    # Validate
                    if not meeting_name or not date or not venue or not city_state or not year_str:
                        errors.append(f"Row {row_num}: Missing required fields")
                        error_count += 1
                        continue

                    year = int(year_str)

                    # Add to database (skip if duplicate)
                    try:
                        self.add_event(meeting_name, date, venue, city_state, year)
                        success_count += 1
                    except sqlite3.IntegrityError:
                        errors.append(f"Row {row_num}: Duplicate event '{meeting_name}'")
                        error_count += 1

                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid year value")
                    error_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    error_count += 1

        except Exception as e:
            errors.append(f"Failed to parse CSV: {str(e)}")
            error_count += 1

        return success_count, error_count, errors

    # ========================================================================
    # MIGRATION
    # ========================================================================

    def migrate_from_hardcoded_events(self, events: List[Event]) -> tuple[int, int]:
        """
        Migrate events from hardcoded list to database

        Args:
            events: List of hardcoded Event objects

        Returns:
            Tuple of (success_count, duplicate_count)
        """
        success_count = 0
        duplicate_count = 0

        for event in events:
            try:
                self.add_event_from_object(event)
                success_count += 1
            except sqlite3.IntegrityError:
                duplicate_count += 1

        return success_count, duplicate_count

    # ========================================================================
    # HELPERS
    # ========================================================================

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> Event:
        """Convert database row to Event object"""
        return Event(
            meeting_name=row['meeting_name'],
            meeting_date_long=row['meeting_date_long'],
            venue=row['venue'],
            city_state=row['city_state']
        )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Singleton instance
_db_instance = None


def get_database() -> EventDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = EventDatabase()
    return _db_instance


def get_events_from_database(year: Optional[int] = None) -> List[Event]:
    """Get events from database (convenience function)"""
    db = get_database()
    return db.get_all_events(year)


def migrate_hardcoded_events():
    """Migrate hardcoded events to database (one-time operation)"""
    from config.events import EVENTS_2025, EVENTS_2026

    db = get_database()

    # Combine all hardcoded events
    all_events = EVENTS_2025 + EVENTS_2026

    success, duplicates = db.migrate_from_hardcoded_events(all_events)

    return success, duplicates
