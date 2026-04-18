# 📧 Streamlit Email Classification Dashboard

A modern, interactive web-based dashboard for the AI Email Classifier Real-time system, built with **Streamlit**, **Plotly**, and **MongoDB**.

## ✨ Features

### 📊 Real-time Statistics
- **Total Email Count**: Track all classified emails
- **Filtered Email Count**: See how many match current filters
- **Average Confidence Score**: Monitor AI classification accuracy
- **High Confidence Emails**: Count of emails with confidence ≥ 80%

### 📈 Interactive Visualizations
- **Classification Distribution Bar Chart**: Visual breakdown by email type
- **Classification Pie Chart**: Percentage distribution
- **Interactive Legend**: Click to toggle visibility
- **Hover Details**: Get exact numbers on hover

### 📬 Smart Email List

#### Quick View Headers
Each email shows:
- Sender email (40 chars)
- Subject line (50 chars)
- Classification label
- 5-second summary (100 chars)
- Confidence score progress bar
- Urgency level emoji

#### Expandable Detailed View
Click to expand any email and see:

**Classification Badge** (Color-coded)
```
Work Email → Green ✓
Spam Email → Red ✗
Promotional → Yellow ⚠
Others → Blue ℹ
```

**Confidence Score** (Visual Progress Bar)
- 0-100% visual indicator
- Percentage display
- Helps identify uncertain classifications

**Urgency Level** (Emoji Indicators)
```
🔴 Critical  - Requires immediate action
🟠 High      - Important, address soon
🟡 Normal    - Standard importance
🟢 Low       - Can wait
```

**5-Second Summary** (AI-Generated)
- Perfect for quick reading
- Extract key points in 5 seconds
- No need to open full email
- Highlighted summary text

**🏷️ Extracted Information (Color-coded Badges)**

The system automatically extracts and highlights important information:

##### ⏰ Deadline Badges (Red)
- Automatically detects dates and time references
- Examples:
  - "Friday" 
  - "2026-04-25"
  - "End of Q1"
  - "Before EOB"
- Helps prioritize time-sensitive emails

##### 💰 Amount Badges (Teal)
- Extracts financial figures
- Examples:
  - "$5,000"
  - "€2,500" 
  - "1000 units"
  - "Budget: $50K"
- Perfect for financial email review

##### 👤 Requester Badges (Yellow)
- Identifies who made the request
- Examples:
  - "John Smith"
  - "Finance Team"
  - "Project Manager"
  - "CEO"
- Know who needs action from

##### Other Entities (Gray)
- Additional extracted information
- Custom entity types
- Confidence scores shown

**📋 Email Metadata**
- Full sender address
- Received date and time
- Complete subject line
- Model version information

### 📋 Quick Summary Table

Compact tabular view with columns:
- From (Sender email)
- Subject (Email title)
- Classification (Type)
- Confidence (0-100%)
- Urgency (Level)
- Date (Received time)

Perfect for scanning all emails quickly!

### 📥 Export Capabilities

**CSV Export**
- Download all displayed emails
- Open in Excel, Google Sheets, etc.
- Perfect for reports and sharing
- Includes all email information

**Statistics Export**
- JSON format detailed stats
- Total email count
- Average confidence
- Classification breakdown

---

## 🎛️ Sidebar Controls

### 1. Classification Filter
**Dropdown Menu**
- All (default)
- work
- personal
- spam
- promotional
- social
- important

Use to focus on specific email types

### 2. Date Range Filter
**Slider: 1-90 days**
- Default: 30 days
- Adjust to see recent or historical data
- Faster queries with shorter ranges

### 3. Email Display Limit
**Slider: 10-500 emails**
- Default: 50 emails
- More emails = slower loading
- Recommended: 20-100 for best performance

### 4. Auto-refresh Interval
**Dropdown Options**
- Manual (no auto-refresh)
- 5 seconds (real-time monitoring)
- 30 seconds (frequent updates)
- 1 minute (balanced)
- 5 minutes (minimal overhead)

Perfect for live monitoring scenarios

### 5. Manual Refresh Button
- Green button: 🔄 Refresh Data
- Instantly fetch latest data
- Bypasses auto-refresh schedule

---

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install streamlit==1.28.1 plotly==5.18.0 pandas==2.1.3

# Or use the startup script
cd scripts
./start_dashboard.sh        # Linux/Mac
powershell .\start_dashboard.ps1  # Windows
```

### Running the Dashboard

```bash
# Method 1: Direct command
streamlit run streamlit_dashboard.py

# Method 2: Using startup script (Linux/Mac)
bash scripts/start_dashboard.sh

# Method 3: Using startup script (Windows)
powershell -ExecutionPolicy Bypass -File scripts/start_dashboard.ps1

# Method 4: Custom port
streamlit run streamlit_dashboard.py --server.port 8502
```

### Access the Dashboard

Open your browser to:
```
http://localhost:8501
```

---

## 📊 Understanding the Dashboard

### Classification Labels Explained

| Label | Color | Meaning |
|-------|-------|---------|
| **WORK** | 🟢 Green | Work-related email |
| **PERSONAL** | 🔵 Blue | Personal communication |
| **SPAM** | 🔴 Red | Unwanted/spam email |
| **PROMOTIONAL** | 🟡 Yellow | Marketing/promotional |
| **SOCIAL** | 🟠 Orange | Social media notification |
| **IMPORTANT** | ⭐ Star | High importance |

### Confidence Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100% | Very confident | Trust classification |
| 70-89% | Confident | Likely correct |
| 50-69% | Moderate | Should verify |
| <50% | Low confidence | Review carefully |

### Urgency Level Guide

| Level | Color | Timeframe | Action |
|-------|-------|-----------|--------|
| 🔴 Critical | Red | Today/Now | Immediate |
| 🟠 High | Orange | 1-2 days | ASAP |
| 🟡 Normal | Yellow | 3-7 days | Standard |
| 🟢 Low | Green | 1-2 weeks | When available |

---

## 💡 Use Cases

### 1. Real-time Email Monitoring
```
1. Set Classification: "All"
2. Set Emails to display: 20
3. Set Auto-refresh: "5 seconds"
4. Watch for new 🔴 Critical emails
5. Click to expand and read summary
```

### 2. Weekly Report Generation
```
1. Filter by date: Last 7 days
2. Filter by classification: "All"
3. Set display: 100 emails
4. Click "Download as CSV"
5. Open in Excel, create charts
6. Send to management
```

### 3. Finding Financial Information
```
1. Filter classification: "work"
2. Expand emails
3. Look for 💰 Amount badges
4. Extract all financial data
5. Export as CSV for finance team
```

### 4. Identifying Deadlines
```
1. Filter classification: "work"
2. Set urgency: "high" or "critical"
3. Look for ⏰ Deadline badges
4. Mark calendar dates
5. Prioritize action items
```

### 5. Model Quality Assessment
```
1. View "Avg. Confidence" metric
2. Find low-confidence emails
3. Manually review classification
4. Check if AI made correct decision
5. Use feedback to improve model
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:
```bash
MONGODB_URL=mongodb://admin:changeme123@mongodb:27017
MONGODB_DB_NAME=email_classifier
```

### Streamlit Configuration

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#FF6B6B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"

[client]
showErrorDetails=true

[server]
maxUploadSize=200
enableXsrfProtection=true
```

---

## 🐛 Troubleshooting

### Dashboard Won't Start
```bash
# Check Python installation
python --version

# Check Streamlit installation
pip list | grep streamlit

# Reinstall Streamlit
pip install --upgrade streamlit
```

### Can't Connect to MongoDB
```bash
# Check MongoDB is running
docker-compose ps

# Start MongoDB
docker-compose up -d mongodb

# Check connection
mongosh mongodb://admin:changeme123@localhost:27017
```

### No Emails Showing
```bash
# Possible reasons:
# 1. Database empty - add test data
python scripts/test_mongodb_api.py

# 2. Date range too narrow - increase to 90 days
# 3. Classification too specific - select "All"
```

### Dashboard Slow
```bash
# Reduce email count to 20-30
# Reduce date range to 7 days
# Increase auto-refresh to 1 minute
# Check MongoDB indexes exist
mongosh mongodb://admin:changeme123@localhost:27017
use email_classifier
db.classified_emails.getIndexes()
```

### Port 8501 Already In Use
```bash
# Use different port
streamlit run streamlit_dashboard.py --server.port 8502

# Or find and kill process using port
# Linux/Mac:
lsof -i :8501
kill -9 <PID>

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

---

## 📊 Dashboard Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Web Interface           │
│  (http://localhost:8501)            │
└──────────────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼─────┐         ┌────▼────┐
    │ Sidebar │         │  Main   │
    │Controls │         │Content  │
    └─────────┘         └────┬────┘
                             │
        ┌────────────────────┼─────────────────┐
        │                    │                 │
    ┌───▼────┐         ┌────▼──────┐     ┌───▼──────┐
    │ Charts │         │   Tables  │     │ Metrics  │
    └────────┘         └───────────┘     └──────────┘
        │                    │                 │
        └────────────────────┼─────────────────┘
                             │
        ┌────────────────────▼─────────────────┐
        │   Motor Async MongoDB Client         │
        │   (Connection Pool)                  │
        └────────────────────┬─────────────────┘
                             │
        ┌────────────────────▼─────────────────┐
        │   MongoDB Database                   │
        │   (email_classifier)                 │
        └──────────────────────────────────────┘
```

---

## 🔗 Integration Points

### With FastAPI Backend
```
FastAPI Endpoint
     ↓
AI Classification
     ↓
MongoDB Save
     ↓
Streamlit Read
     ↓
Dashboard Display
```

### Real-time Sync
- Both FastAPI and Streamlit use same MongoDB database
- Changes in FastAPI immediately visible in dashboard
- Auto-refresh keeps dashboard current

---

## 📱 Mobile & Responsive

Dashboard works on:
- ✅ Desktop (Full features)
- ✅ Tablet (Responsive layout)
- ✅ Mobile (Adapted interface)

Streamlit automatically adjusts for screen size

---

## 🎨 Customization

### Color Scheme

Edit HTML/CSS in `streamlit_dashboard.py`:
```python
st.markdown("""
    <style>
    .deadline-badge {
        background-color: #ff6b6b;  # Red
        color: white;
    }
    .amount-badge {
        background-color: #4ecdc4;  # Teal
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
```

### Add Custom Metrics

Add new metric cards:
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Custom Metric", value, delta)
```

---

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.28.1 | Web framework |
| plotly | 5.18.0 | Interactive charts |
| pandas | 2.1.3 | Data manipulation |
| motor | 3.3.2 | Async MongoDB driver |
| python-dotenv | 1.0.0 | Environment variables |

---

## 🚀 Performance Tips

1. **Set reasonable limits**
   - Max 100 emails per page
   - Max 30-day date range

2. **Optimize refresh rate**
   - 5 seconds for live monitoring
   - 30-60 seconds for normal use
   - 5 minutes for background monitoring

3. **Ensure MongoDB indexes**
   ```bash
   db.classified_emails.createIndex({"created_at": -1})
   db.classified_emails.createIndex({"classification_label": 1})
   ```

4. **Use classification filter**
   - Narrow results to specific types
   - Reduces data transfer

5. **Close unused tabs**
   - Each Streamlit session uses resources
   - Close when not actively using

---

## 🎯 What's Next

After setting up the dashboard:

1. ✅ Populate MongoDB with classified emails
2. ✅ Monitor classification accuracy
3. ✅ Review extracted entities
4. ✅ Generate weekly reports
5. ✅ Fine-tune AI model based on feedback
6. ✅ Deploy to production server

---

## 📞 Support & Troubleshooting

**See also:**
- `STREAMLIT_DASHBOARD_GUIDE.md` - Complete feature guide
- `STREAMLIT_QUICKSTART.md` - Quick setup guide
- `MONGODB_FASTAPI_GUIDE.md` - Backend integration
- `MONGODB_INTEGRATION_SUMMARY.md` - Database setup

---

## 📄 License & Credits

Part of the **AI Email Classifier Real-time** system.

Built with:
- Streamlit for interactive UI
- Plotly for beautiful visualizations
- MongoDB for data persistence
- Motor for async operations

---

**Ready to visualize your emails?** Run: `streamlit run streamlit_dashboard.py` 🚀
