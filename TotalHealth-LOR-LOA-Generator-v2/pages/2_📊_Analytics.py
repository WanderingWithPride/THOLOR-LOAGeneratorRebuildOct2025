"""
Analytics Dashboard - Total Health Conferencing
Document generation tracking, revenue insights, and usage trends
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict

from core.security import require_authentication, AuthenticationManager
from config.settings import LOGGING_CONFIG

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Require authentication
require_authentication()

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Analytics Dashboard")
st.markdown("Document generation insights and trends")

# ============================================================================
# LOAD ACTIVITY LOG
# ============================================================================

log_file = Path(LOGGING_CONFIG["log_file"])

def load_activity_log() -> List[Dict]:
    """Load activity log from JSON file"""
    if not log_file.exists():
        return []

    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except Exception:
        return []

activity_log = load_activity_log()

# ============================================================================
# SUMMARY METRICS
# ============================================================================

st.subheader("📈 Summary")

# Calculate metrics
total_documents = len(activity_log)
total_revenue = sum(entry.get('total_cost', 0) for entry in activity_log)
unique_companies = len(set(entry.get('company_name', '') for entry in activity_log))

# Time range
if activity_log:
    timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in activity_log if 'timestamp' in entry]
    if timestamps:
        earliest = min(timestamps)
        latest = max(timestamps)
        days_active = (latest - earliest).days + 1
    else:
        days_active = 1
else:
    days_active = 1

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Documents", total_documents)

with col2:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col3:
    st.metric("Unique Companies", unique_companies)

with col4:
    avg_per_doc = total_revenue / total_documents if total_documents > 0 else 0
    st.metric("Avg per Document", f"${avg_per_doc:,.2f}")

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "💰 Revenue",
    "📅 Events",
    "👥 Companies"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.subheader("Document Generation Overview")

    if not activity_log:
        st.info("No activity data available yet. Generate some documents to see analytics!")
    else:
        # Document type breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📄 Document Types")
            doc_types = defaultdict(int)
            for entry in activity_log:
                doc_type = entry.get('document_type', 'Unknown')
                doc_types[doc_type] += 1

            for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_documents) * 100
                st.metric(doc_type, count, f"{percentage:.1f}%")

        with col2:
            st.markdown("### 🎯 Generation Modes")
            modes = defaultdict(int)
            for entry in activity_log:
                mode = entry.get('mode', 'single-event')
                modes[mode] += 1

            for mode, count in sorted(modes.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_documents) * 100
                mode_display = mode.replace('-', ' ').title()
                st.metric(mode_display, count, f"{percentage:.1f}%")

        # User activity
        st.markdown("---")
        st.markdown("### 👤 User Activity")

        user_activity = defaultdict(int)
        for entry in activity_log:
            user = entry.get('user_role', 'Unknown')
            user_activity[user] += 1

        col1, col2, col3 = st.columns(3)

        for idx, (user, count) in enumerate(sorted(user_activity.items(), key=lambda x: x[1], reverse=True)):
            with [col1, col2, col3][idx % 3]:
                st.metric(user, count)

# ============================================================================
# TAB 2: REVENUE
# ============================================================================

with tab2:
    st.subheader("💰 Revenue Analysis")

    if not activity_log:
        st.info("No revenue data available yet.")
    else:
        # Revenue by event
        st.markdown("### Top Events by Revenue")

        event_revenue = defaultdict(float)
        for entry in activity_log:
            event = entry.get('meeting_name', 'Unknown')
            revenue = entry.get('total_cost', 0)
            event_revenue[event] += revenue

        # Display top 10
        top_events = sorted(event_revenue.items(), key=lambda x: x[1], reverse=True)[:10]

        for idx, (event, revenue) in enumerate(top_events, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{idx}. {event}**")
            with col2:
                st.markdown(f"**${revenue:,.2f}**")

        st.markdown("---")

        # Booth selections
        st.markdown("### 💼 Booth Selections")

        booth_counts = defaultdict(int)
        booth_revenue = defaultdict(float)

        for entry in activity_log:
            booth = entry.get('booth_selected', 'None')
            if booth and booth != 'None':
                booth_counts[booth] += 1
                booth_revenue[booth] += entry.get('total_cost', 0)

        if booth_counts:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Count**")
                for booth, count in sorted(booth_counts.items(), key=lambda x: x[1], reverse=True):
                    st.metric(booth, count)

            with col2:
                st.markdown("**Revenue**")
                for booth, revenue in sorted(booth_revenue.items(), key=lambda x: x[1], reverse=True):
                    st.metric(booth, f"${revenue:,.2f}")

# ============================================================================
# TAB 3: EVENTS
# ============================================================================

with tab3:
    st.subheader("📅 Event Analytics")

    if not activity_log:
        st.info("No event data available yet.")
    else:
        # Event popularity
        st.markdown("### Most Popular Events")

        event_counts = defaultdict(int)
        for entry in activity_log:
            event = entry.get('meeting_name', 'Unknown')
            event_counts[event] += 1

        # Top 15 events
        top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        for idx, (event, count) in enumerate(top_events, 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{idx}. **{event}**")
            with col2:
                st.metric("Documents", count)

        st.markdown("---")

        # Add-ons analysis
        st.markdown("### 📦 Add-Ons Analysis")

        addon_counts = defaultdict(int)
        for entry in activity_log:
            addons = entry.get('add_ons', [])
            for addon in addons:
                addon_counts[addon] += 1

        if addon_counts:
            st.markdown("**Most Popular Add-Ons:**")
            for addon, count in sorted(addon_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                st.metric(addon, count)
        else:
            st.info("No add-ons selected yet.")

# ============================================================================
# TAB 4: COMPANIES
# ============================================================================

with tab4:
    st.subheader("👥 Company Analytics")

    if not activity_log:
        st.info("No company data available yet.")
    else:
        # Company activity
        st.markdown("### Most Active Companies")

        company_activity = defaultdict(lambda: {'count': 0, 'revenue': 0})

        for entry in activity_log:
            company = entry.get('company_name', 'Unknown')
            company_activity[company]['count'] += 1
            company_activity[company]['revenue'] += entry.get('total_cost', 0)

        # Sort by count
        top_companies = sorted(
            company_activity.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]

        for idx, (company, data) in enumerate(top_companies, 1):
            with st.expander(f"{idx}. {company}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Documents", data['count'])

                with col2:
                    st.metric("Total Revenue", f"${data['revenue']:,.2f}")

                with col3:
                    avg = data['revenue'] / data['count'] if data['count'] > 0 else 0
                    st.metric("Avg per Doc", f"${avg:,.2f}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"📊 Total Documents: {total_documents}")

with col2:
    st.caption(f"💰 Total Revenue: ${total_revenue:,.2f}")

with col3:
    if activity_log:
        latest_entry = max(activity_log, key=lambda x: x.get('timestamp', ''))
        latest_time = latest_entry.get('timestamp', 'Unknown')
        st.caption(f"🕐 Last Updated: {latest_time[:10]}")
    else:
        st.caption("🕐 Last Updated: Never")
