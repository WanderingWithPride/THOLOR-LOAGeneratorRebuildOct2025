"""
Event Management Page - Total Health Conferencing
Admin interface for managing event calendar
"""
import streamlit as st
from services.event_database import (
    get_database,
    migrate_hardcoded_events,
    get_events_from_database
)
from config.events import Event
from core.security import require_authentication, AuthenticationManager

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Event Management",
    page_icon="📅",
    layout="wide"
)

# Require authentication
require_authentication()

# Check admin privileges
if not AuthenticationManager.is_admin():
    st.error("🔒 Admin access required")
    st.info("This page is only available to administrators.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("📅 Event Calendar Management")
st.markdown("Manage events for LOR/LOA generation")

# Initialize database
db = get_database()

# ============================================================================
# STATISTICS
# ============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Events", db.count_events())

with col2:
    years = db.get_years()
    st.metric("Years", len(years))

with col3:
    current_year = 2025
    current_year_count = len(db.get_all_events(year=current_year))
    st.metric(f"{current_year} Events", current_year_count)

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 View Events",
    "➕ Add Event",
    "📤 Import/Export",
    "🔧 Migration"
])

# ============================================================================
# TAB 1: VIEW EVENTS
# ============================================================================

with tab1:
    st.subheader("📋 All Events")

    # Filter by year
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input("🔍 Search events", placeholder="Enter event name...")

    with col2:
        filter_year = st.selectbox(
            "Filter by Year",
            options=["All Years"] + [str(y) for y in sorted(db.get_years(), reverse=True)]
        )

    # Get events
    if search_query:
        events = db.search_events(search_query)
    elif filter_year != "All Years":
        events = db.get_all_events(year=int(filter_year))
    else:
        events = db.get_all_events()

    st.info(f"📊 Showing {len(events)} events")

    # Display events in table
    if events:
        for event in events:
            with st.expander(f"📅 {event.meeting_name} ({event.get_year()})"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Date:** {event.meeting_date_long}")
                    st.markdown(f"**Venue:** {event.venue}")
                    st.markdown(f"**Location:** {event.city_state}")
                    st.markdown(f"**Year:** {event.get_year()}")

                with col2:
                    # Get event from DB to get ID
                    db_event = db.get_event_by_name(event.meeting_name)

                    if db_event and st.button(f"🗑️ Delete", key=f"del_{event.meeting_name}"):
                        # We need the ID from the database
                        # For now, delete by name matching
                        st.warning("Delete functionality requires event ID from database")

    else:
        st.info("No events found. Add events or import from CSV.")

# ============================================================================
# TAB 2: ADD EVENT
# ============================================================================

with tab2:
    st.subheader("➕ Add New Event")

    with st.form("add_event_form"):
        meeting_name = st.text_input(
            "Event Name*",
            placeholder="e.g., ASCO Direct from Chicago 2025"
        )

        col1, col2 = st.columns(2)

        with col1:
            meeting_date = st.text_input(
                "Date*",
                placeholder="e.g., May 30 - June 3, 2025"
            )

            venue = st.text_input(
                "Venue*",
                placeholder="e.g., McCormick Place"
            )

        with col2:
            city_state = st.text_input(
                "City, State*",
                placeholder="e.g., Chicago, IL"
            )

            year = st.number_input(
                "Year*",
                min_value=2024,
                max_value=2030,
                value=2025,
                step=1
            )

        submitted = st.form_submit_button("➕ Add Event", type="primary")

        if submitted:
            if not meeting_name or not meeting_date or not venue or not city_state:
                st.error("❌ Please fill in all required fields")
            else:
                try:
                    event_id = db.add_event(
                        meeting_name=meeting_name,
                        meeting_date_long=meeting_date,
                        venue=venue,
                        city_state=city_state,
                        year=year
                    )
                    st.success(f"✅ Event added successfully! (ID: {event_id})")
                    st.balloons()
                except Exception as e:
                    if "UNIQUE constraint" in str(e):
                        st.error("❌ Event with this name already exists")
                    else:
                        st.error(f"❌ Failed to add event: {str(e)}")

# ============================================================================
# TAB 3: IMPORT/EXPORT
# ============================================================================

with tab3:
    st.subheader("📤 Import/Export Events")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 Import from CSV")

        st.markdown("""
        **CSV Format:**
        - Meeting Name
        - Date
        - Venue
        - City/State
        - Year
        """)

        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload a CSV file with event data"
        )

        if uploaded_file:
            if st.button("📥 Import Events", type="primary"):
                with st.spinner("Importing events..."):
                    success, errors, error_msgs = db.import_from_csv(uploaded_file)

                if success > 0:
                    st.success(f"✅ Imported {success} events successfully!")

                if errors > 0:
                    st.warning(f"⚠️ {errors} errors occurred")
                    with st.expander("View Errors"):
                        for msg in error_msgs:
                            st.error(msg)

    with col2:
        st.markdown("### 📤 Export to CSV")

        st.markdown("""
        Download all events as CSV file for:
        - Backup
        - Editing in Excel
        - Sharing with team
        """)

        if st.button("📤 Export All Events"):
            csv_buffer = db.export_to_csv()

            st.download_button(
                "📥 Download CSV",
                data=csv_buffer,
                file_name=f"events_export_{db.count_events()}_events.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================================================
# TAB 4: MIGRATION
# ============================================================================

with tab4:
    st.subheader("🔧 Database Migration")

    st.info("""
    **One-Time Migration**

    This will migrate all hardcoded events from `config/events.py` to the database.
    Run this once when first setting up the event calendar system.
    """)

    if st.button("🚀 Migrate Hardcoded Events", type="primary"):
        with st.spinner("Migrating events..."):
            success, duplicates = migrate_hardcoded_events()

        st.success(f"✅ Migration complete!")
        st.metric("Events Added", success)
        st.metric("Duplicates Skipped", duplicates)

        st.info("You can now use the database for event management and eventually remove hardcoded events.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption(f"Event Management System | Total Events: {db.count_events()}")
