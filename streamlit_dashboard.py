"""
Streamlit Dashboard for AI Email Classification System
Real-time email monitoring and classification display
"""

import streamlit as st
import pandas as pd
import asyncio
import nest_asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import plotly.graph_objects as go
import plotly.express as px
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Apply nest_asyncio to allow nested event loops (fixes "Event loop is closed" error)
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:changeme123@mongodb:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "email_classifier")

# Page Configuration
st.set_page_config(
    page_title="Email Classification Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .summary-text {
        font-size: 14px;
        line-height: 1.6;
        color: #333;
    }
    .entity-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .deadline-badge {
        background-color: #ff6b6b;
        color: white;
    }
    .amount-badge {
        background-color: #4ecdc4;
        color: white;
    }
    .requester-badge {
        background-color: #ffd93d;
        color: #333;
    }
    .confidence-high {
        background-color: #51cf66;
        color: white;
    }
    .confidence-medium {
        background-color: #ffd93d;
        color: #333;
    }
    .confidence-low {
        background-color: #ff8c42;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


# ===================== MongoDB Connection =====================
class MongoDBClient:
    """MongoDB async client for Streamlit"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance
    
    async def connect(self):
        """Connect to MongoDB"""
        if self.client is None:
            try:
                self.client = AsyncIOMotorClient(
                    MONGODB_URL,
                    maxPoolSize=50,
                    minPoolSize=10,
                    serverSelectionTimeoutMS=5000,
                    socketTimeoutMS=30000,
                    connectTimeoutMS=10000
                )
                # Test connection
                await self.client.admin.command('ping')
                self.db = self.client[MONGODB_DB_NAME]
                st.session_state.mongo_connected = True
                return True
            except Exception as e:
                st.error(f"❌ MongoDB Connection Failed: {str(e)}")
                st.session_state.mongo_connected = False
                return False
        return True
    
    async def get_classified_emails(
        self,
        classification_label: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
        days_back: int = 30
    ) -> List[Dict]:
        """Fetch classified emails from MongoDB"""
        try:
            collection = self.db["classified_emails"]
            
            # Build query
            query = {}
            if classification_label and classification_label != "All":
                query["classification_label"] = classification_label
            
            # Date filter
            date_threshold = datetime.utcnow() - timedelta(days=days_back)
            query["created_at"] = {"$gte": date_threshold}
            
            # Fetch emails
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            emails = await cursor.to_list(length=limit)
            
            return emails
        except Exception as e:
            st.error(f"❌ Error fetching emails: {str(e)}")
            return []
    
    async def get_statistics(self) -> Dict:
        """Get email statistics"""
        try:
            collection = self.db["classified_emails"]
            
            # Total emails
            total = await collection.count_documents({})
            
            # Count by classification
            pipeline = [
                {
                    "$group": {
                        "_id": "$classification_label",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            classification_stats = []
            async for doc in collection.aggregate(pipeline):
                classification_stats.append(doc)
            
            # Average confidence score
            confidence_pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                }
            ]
            
            avg_confidence = 0
            async for doc in collection.aggregate(confidence_pipeline):
                avg_confidence = doc.get("avg_confidence", 0)
            
            return {
                "total_emails": total,
                "classification_stats": classification_stats,
                "avg_confidence": avg_confidence
            }
        except Exception as e:
            st.error(f"❌ Error fetching statistics: {str(e)}")
            return {}


# ===================== Helper Functions =====================
def get_mongo_client() -> MongoDBClient:
    """Get MongoDB client instance - cached by Streamlit"""
    return MongoDBClient()


@st.cache_data(ttl=30)
def fetch_emails_cached(
    classification_label: Optional[str] = None,
    days_back: int = 30,
    limit: int = 100
) -> tuple:
    """Fetch emails with caching (30 second TTL)"""
    try:
        emails = asyncio.run(fetch_emails_async(
            classification_label=classification_label,
            days_back=days_back,
            limit=limit
        ))
        return emails, True
    except Exception as e:
        return [], False


@st.cache_data(ttl=30)
def fetch_statistics_cached() -> tuple:
    """Fetch statistics with caching (30 second TTL)"""
    try:
        stats = asyncio.run(fetch_statistics_async())
        return stats, True
    except Exception as e:
        return {}, False


def format_confidence_badge(score: float) -> str:
    """Format confidence score as HTML badge"""
    if score >= 0.8:
        css_class = "confidence-high"
        label = "High"
    elif score >= 0.6:
        css_class = "confidence-medium"
        label = "Medium"
    else:
        css_class = "confidence-low"
        label = "Low"
    
    return f'<span class="entity-badge {css_class}">{label} ({score:.2%})</span>'


def format_entities_html(entities: List[Dict]) -> str:
    """Format extracted entities as HTML badges"""
    html = ""
    
    for entity in entities:
        entity_type = entity.get("entity_type", "").lower()
        value = entity.get("value", "")
        confidence = entity.get("confidence", 1.0)
        
        if entity_type == "deadline":
            html += f'<span class="entity-badge deadline-badge">⏰ {value}</span>'
        elif entity_type == "amount":
            html += f'<span class="entity-badge amount-badge">💰 {value}</span>'
        elif entity_type == "requester":
            html += f'<span class="entity-badge requester-badge">👤 {value}</span>'
        else:
            html += f'<span class="entity-badge" style="background-color: #95a5a6; color: white;">🏷️ {value}</span>'
    
    return html if html else '<span style="color: #999;">No entities extracted</span>'


def get_urgency_color(urgency_level: str) -> str:
    """Get color for urgency level"""
    colors = {
        "critical": "🔴",
        "high": "🟠",
        "normal": "🟡",
        "low": "🟢"
    }
    return colors.get(urgency_level, "⚪")


def format_datetime(dt) -> str:
    """Format datetime for display"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def fetch_emails_async(
    classification_label: Optional[str] = None,
    days_back: int = 30,
    limit: int = 100
) -> List[Dict]:
    """Async wrapper for fetching emails"""
    mongo = get_mongo_client()
    await mongo.connect()
    return await mongo.get_classified_emails(
        classification_label=classification_label,
        limit=limit,
        days_back=days_back
    )


async def fetch_statistics_async() -> Dict:
    """Async wrapper for fetching statistics"""
    mongo = get_mongo_client()
    await mongo.connect()
    return await mongo.get_statistics()


# ===================== Dashboard Layout =====================
def main():
    """Main Streamlit app"""
    
    # Initialize session state
    if "mongo_connected" not in st.session_state:
        st.session_state.mongo_connected = False
    
    # Title and Header
    st.title("📧 Email Classification Dashboard")
    st.markdown("Real-time AI-powered email classification and monitoring system")
    
    # Status information
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"✅ **Dashboard Status**: Connected to MongoDB")
    with col2:
        st.markdown(f"🔄 **Cache TTL**: 30 seconds")
    with col3:
        st.markdown(f"⏰ **Last Update**: {datetime.now().strftime('%H:%M:%S')}")
    
    st.divider()
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Dashboard Settings")
        
        # Classification Filter
        classification_filter = st.selectbox(
            "Filter by Classification",
            ["All", "work", "personal", "spam", "promotional", "social", "important"]
        )
        
        # Days back filter
        days_back = st.slider(
            "Show emails from last (days)",
            min_value=1,
            max_value=90,
            value=30,
            step=1
        )
        
        # Display limit
        display_limit = st.slider(
            "Number of emails to display",
            min_value=10,
            max_value=500,
            value=50,
            step=10
        )
        
        # Refresh interval
        refresh_interval = st.selectbox(
            "Auto-refresh interval",
            ["Manual", "5 seconds", "30 seconds", "1 minute", "5 minutes"]
        )

        # Map selection to seconds
        refresh_map = {
            "Manual": 0,
            "5 seconds": 5,
            "30 seconds": 30,
            "1 minute": 60,
            "5 minutes": 300,
        }
        refresh_seconds = refresh_map.get(refresh_interval, 0)

        st.divider()

        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

        # Auto-refresh via HTML meta tag (works reliably and doesn't block event loop)
        if refresh_seconds and refresh_seconds > 0:
            # Insert a meta refresh so the browser reloads the page automatically
            st.markdown(f"<meta http-equiv=\"refresh\" content=\"{refresh_seconds}\">", unsafe_allow_html=True)
            st.markdown(f"Auto-refresh enabled — reloading every {refresh_seconds} seconds.")
            # Clear cached data so each reload fetches fresh results from MongoDB
            try:
                st.cache_data.clear()
            except Exception:
                # Fallback: ignore if cache clearing isn't available
                pass
    
    # Main content area
    try:
        # Fetch data with caching
        emails, emails_ok = fetch_emails_cached(
            classification_label=classification_filter if classification_filter != "All" else None,
            days_back=days_back,
            limit=display_limit
        )
        
        stats, stats_ok = fetch_statistics_cached()
        
        # Check if fetch was successful
        if not emails_ok or not stats_ok:
            st.error("⚠️ Failed to fetch data from MongoDB. Please check your connection.")
            return
        
        if not emails:
            st.warning("⚠️ No emails found. Please check your filters or database connection.")
            return
        
        # ==================== Statistics Section ====================
        st.header("📊 Overview Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Emails",
                stats.get("total_emails", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "Shown Emails",
                len(emails),
                delta=None
            )
        
        with col3:
            avg_confidence = stats.get("avg_confidence", 0)
            st.metric(
                "Avg. Confidence",
                f"{avg_confidence:.2%}",
                delta=None
            )
        
        with col4:
            high_confidence = len([e for e in emails if e.get("confidence_score", 0) >= 0.8])
            st.metric(
                "High Confidence Emails",
                high_confidence,
                delta=None
            )
        
        st.divider()
        
        # ==================== Classification Chart ====================
        st.header("📈 Classification Distribution")
        
        if stats.get("classification_stats"):
            chart_data = {
                "Label": [item["_id"] for item in stats["classification_stats"]],
                "Count": [item["count"] for item in stats["classification_stats"]]
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                fig_bar = px.bar(
                    x=chart_data["Label"],
                    y=chart_data["Count"],
                    title="Email Count by Classification",
                    labels={"x": "Classification", "y": "Count"},
                    color=chart_data["Label"],
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Pie chart
                fig_pie = px.pie(
                    values=chart_data["Count"],
                    names=chart_data["Label"],
                    title="Classification Distribution"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        
        # ==================== Email List Table ====================
        st.header("📬 Email List")
        
        # Create DataFrame for display
        display_data = []
        
        for idx, email in enumerate(emails, 1):
            # Extract entities HTML
            entities = email.get("extracted_entities", [])
            entities_html = format_entities_html(entities)
            
            # Get urgency level
            sentiment = email.get("sentiment_analysis", {})
            urgency = sentiment.get("urgency_level", "normal")
            urgency_emoji = get_urgency_color(urgency)
            
            display_data.append({
                "#": idx,
                "From": email.get("sender", "Unknown")[:40],
                "Subject": email.get("subject", "No Subject")[:50],
                "Classification": email.get("classification_label", "unknown").upper(),
                "Summary": email.get("summary", "No summary available")[:100],
                "Extracted Info": entities_html,
                "Confidence": email.get("confidence_score", 0),
                "Urgency": f"{urgency_emoji} {urgency.upper()}",
                "Date": format_datetime(email.get("created_at", datetime.utcnow()))
            })
        
        # Display as table with columns
        st.subheader(f"Showing {len(display_data)} emails")
        
        # Create interactive table view
        for idx, row_data in enumerate(display_data):
            # Create expandable container for each email
            with st.expander(
                f"📧 {row_data['From'][:30]} - {row_data['Subject'][:40]}...",
                expanded=False
            ):
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.markdown("**Classification**")
                    label = row_data['Classification']
                    if label == "WORK":
                        st.success(label)
                    elif label == "SPAM":
                        st.error(label)
                    elif label == "PROMOTIONAL":
                        st.warning(label)
                    else:
                        st.info(label)
                
                with col2:
                    st.markdown("**Confidence Score**")
                    confidence = row_data['Confidence']
                    st.progress(confidence, text=f"{confidence:.2%}")
                
                with col3:
                    st.markdown("**Urgency Level**")
                    st.markdown(row_data['Urgency'])
                
                st.divider()
                
                # Summary section
                st.markdown("**📝 5-Second Summary**")
                st.markdown(f'<p class="summary-text">{row_data["Summary"]}</p>', unsafe_allow_html=True)
                
                # Extracted Entities
                st.markdown("**🏷️ Extracted Information**")
                st.markdown(row_data['Extracted Info'], unsafe_allow_html=True)
                
                # Additional Info
                st.markdown("**ℹ️ Email Details**")
                email_detail_col1, email_detail_col2 = st.columns(2)
                
                with email_detail_col1:
                    st.text(f"From: {row_data['From']}")
                    st.text(f"Date: {row_data['Date']}")
                
                with email_detail_col2:
                    st.text(f"Subject: {row_data['Subject']}")
                    original_email = emails[idx]
                    if original_email.get("model_version"):
                        st.text(f"Model: {original_email.get('model_version', 'N/A')}")
        
        st.divider()
        
        # ==================== Summary Table ====================
        st.subheader("📋 Quick Summary Table")
        
        # Create simplified dataframe for quick view
        summary_df = pd.DataFrame([
            {
                "From": row["From"],
                "Subject": row["Subject"],
                "Classification": row["Classification"],
                "Confidence": f"{row['Confidence']:.1%}",
                "Urgency": row["Urgency"],
                "Date": row["Date"]
            }
            for row in display_data
        ])
        
        # Display table with custom styling
        st.dataframe(
            summary_df,
            use_container_width=True,
            height=400
        )
        
        # ==================== Export Options ====================
        st.divider()
        st.subheader("📥 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export as CSV
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export as Excel would require openpyxl - show info instead
            st.info("💡 Install openpyxl for Excel export: `pip install openpyxl`")
        
        with col3:
            # Summary stats
            if st.button("📊 Show Detailed Statistics", use_container_width=True):
                st.json({
                    "Total Emails": stats.get("total_emails", 0),
                    "Average Confidence": f"{stats.get('avg_confidence', 0):.2%}",
                    "Classification Breakdown": {
                        item["_id"]: item["count"]
                        for item in stats.get("classification_stats", [])
                    }
                })
        
        # ==================== Footer ====================
        st.divider()
        st.markdown("""
        ---
        **🔧 Dashboard Settings:**
        - Filter by classification and date range using the sidebar
        - Click on emails to view full details and extracted information
        - Use the refresh button to fetch the latest data
        - Export data in CSV format for further analysis
        
        **📌 Key Features:**
        - Real-time email classification display
        - AI-powered summary for quick reading
        - Automatic entity extraction (deadlines, amounts, requesters)
        - Urgency level indicators
        - Classification confidence scores
        - Interactive visualization charts
        
        Last updated: {lastupdate}
        """.format(lastupdate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("""
        💡 **Troubleshooting Tips:**
        1. Make sure MongoDB is running: `docker-compose ps`
        2. Check MongoDB logs: `docker-compose logs mongodb`
        3. Verify connection string in .env file
        4. Ensure MONGODB_URL is accessible from your network
        5. Try refreshing the page (F5)
        
        **Common Issues:**
        - "Event loop is closed" → Click refresh button or restart dashboard
        - "No emails found" → Add sample data: `python scripts/test_mongodb_api.py`
        - "Connection refused" → Start MongoDB: `docker-compose up -d mongodb`
        """)


if __name__ == "__main__":
    main()
