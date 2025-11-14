"""
Audit Trail Viewer Page
Displays activity log for transparency and accountability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils.audit_utils import (
    get_audit_log,
    format_audit_log_df,
    get_audit_statistics,
    clear_audit_log,
    initialize_session
)


def local_css():
    st.markdown(
        """
        <style>
            .audit-header {
                background: linear-gradient(90deg, #6a1b9a, #8e24aa);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .audit-header h1 {
                color: white;
                margin: 0;
                font-size: 2.2rem;
            }
            .audit-header p {
                color: #f1f1f1;
                margin: 0;
                font-size: 1.05rem;
            }
            .stat-card {
                background: white;
                border-left: 5px solid #8e24aa;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_audit_page():
    local_css()
    initialize_session()

    # Header
    st.markdown(
        """
        <div class="audit-header">
            <h1>📋 Audit Trail</h1>
            <p>Log aktivitas dan transparansi penggunaan dashboard PAD</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # About audit trail
    with st.expander("ℹ️ Tentang Audit Trail"):
        st.markdown("""
        ### 📚 Apa itu Audit Trail?

        **Audit Trail** adalah catatan kronologis dari semua aktivitas yang terjadi di dashboard PAD.
        Sistem ini meningkatkan **transparansi** dan **akuntabilitas** dengan mendokumentasikan:

        - **Model Runs**: Setiap kali model regresi dijalankan
        - **Projections**: Perhitungan proyeksi PAD
        - **Data Loads**: Pemuatan data historis
        - **Scenario Saves**: Penyimpanan skenario what-if
        - **Exports**: Unduhan laporan dan data
        - **Sessions**: Sesi pengguna yang mengakses dashboard

        **Manfaat:**
        - 🔍 Transparansi proses pengambilan keputusan
        - 📊 Tracking penggunaan dashboard
        - 🔒 Keamanan dan accountability
        - 📈 Analisis pola penggunaan
        """)

    # Get statistics
    stats = get_audit_statistics()

    # Display statistics
    st.header("📊 Statistik Audit")

    if stats['total_events'] == 0:
        st.info("📭 Belum ada aktivitas yang tercatat dalam audit log.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Events", f"{stats['total_events']:,}")

    with col2:
        st.metric("Unique Users", stats['unique_users'])

    with col3:
        st.metric("Unique Sessions", stats['unique_sessions'])

    with col4:
        st.metric("Event Types", len(stats['event_types']))

    # Time range
    st.caption(f"📅 Periode: {stats['first_event']} sampai {stats['last_event']}")

    # Event type breakdown
    st.markdown("---")
    st.subheader("📈 Breakdown by Event Type")

    if stats['event_types']:
        # Create pie chart
        fig_pie = px.pie(
            names=list(stats['event_types'].keys()),
            values=list(stats['event_types'].values()),
            title="Distribusi Tipe Event"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

        # Bar chart
        fig_bar = go.Figure(data=[
            go.Bar(
                x=list(stats['event_types'].keys()),
                y=list(stats['event_types'].values()),
                marker_color='#8e24aa',
                text=list(stats['event_types'].values()),
                textposition='outside'
            )
        ])
        fig_bar.update_layout(
            title="Jumlah Event per Tipe",
            xaxis_title="Tipe Event",
            yaxis_title="Jumlah",
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Audit log viewer
    st.markdown("---")
    st.header("🔍 Audit Log Viewer")

    # Filters
    col1, col2 = st.columns([2, 1])

    with col1:
        event_type_filter = st.selectbox(
            "Filter by Event Type",
            ["All"] + list(stats['event_types'].keys())
        )

    with col2:
        limit = st.number_input(
            "Number of Records",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )

    # Get filtered log
    if event_type_filter == "All":
        log_data = get_audit_log(limit=limit)
    else:
        log_data = get_audit_log(event_type=event_type_filter, limit=limit)

    # Display log
    if log_data:
        log_df = format_audit_log_df(log_data)
        st.dataframe(log_df, use_container_width=True, hide_index=True, height=400)

        # Export log
        st.download_button(
            label="📥 Download Audit Log (CSV)",
            data=log_df.to_csv(index=False).encode('utf-8'),
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No events found matching the filters.")

    # Timeline visualization
    if log_data and len(log_data) > 1:
        st.markdown("---")
        st.subheader("📈 Activity Timeline")

        # Convert to DataFrame for timeline
        df_timeline = pd.DataFrame(log_data)
        df_timeline['timestamp'] = pd.to_datetime(df_timeline['timestamp'])
        df_timeline['date'] = df_timeline['timestamp'].dt.date
        df_timeline['hour'] = df_timeline['timestamp'].dt.hour

        # Events per day
        daily_counts = df_timeline.groupby('date').size().reset_index(name='count')
        fig_timeline = px.line(
            daily_counts,
            x='date',
            y='count',
            title='Activity Over Time (Events per Day)',
            markers=True
        )
        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Events",
            template="plotly_white"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        # Events per hour of day
        hourly_counts = df_timeline.groupby('hour').size().reset_index(name='count')
        fig_hourly = px.bar(
            hourly_counts,
            x='hour',
            y='count',
            title='Activity by Hour of Day',
            labels={'hour': 'Hour (24h)', 'count': 'Number of Events'}
        )
        fig_hourly.update_layout(template="plotly_white")
        st.plotly_chart(fig_hourly, use_container_width=True)

    # Admin actions
    st.markdown("---")
    st.header("🔧 Admin Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh Statistics"):
            st.rerun()

    with col2:
        if st.button("🗑️ Clear Audit Log", type="secondary"):
            st.warning("⚠️ This will permanently delete all audit log entries!")
            confirm = st.checkbox("I confirm I want to clear the log")
            if confirm:
                if clear_audit_log():
                    st.success("✅ Audit log cleared successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear audit log")

    # Footer
    st.markdown("---")
    st.caption("💡 **Tips**: Audit trail membantu memastikan transparansi dan akuntabilitas dalam proses proyeksi PAD. "
               "Simpan audit log secara berkala untuk dokumentasi.")


def app():
    show_audit_page()


if __name__ == "__main__":
    app()
