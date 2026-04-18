# Streamlit Email Classification Dashboard - User Guide

## 📋 Overview

The Streamlit Dashboard provides a real-time, interactive web interface to monitor and manage classified emails from the AI Email Classifier system. It offers:

- 📊 Real-time statistics and visualization
- 📧 Interactive email list with detailed information
- 🏷️ Highlighted extracted entities (deadlines, amounts, requesters)
- 📝 AI-generated 5-second summaries
- 🎯 Classification confidence scores
- 🚨 Urgency level indicators
- 📥 Data export capabilities

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Streamlit and visualization libraries
pip install streamlit==1.28.1 plotly==5.18.0 pandas==2.1.3

# Or install all requirements
pip install -r requirements.txt
```

### 2. Start MongoDB (if not already running)

```bash
# Using Docker Compose
docker-compose up -d mongodb

# Or check status
docker-compose ps
```

### 3. Run the Dashboard

```bash
# Navigate to project directory
cd "e:\PJ Data\AI_Email_Classifier_Real-time"

# Run Streamlit app
streamlit run streamlit_dashboard.py
```

The dashboard will open automatically in your browser at:
```
http://localhost:8501
```

---

## 🎨 Dashboard Features

### 📊 Overview Statistics Section

Displays key metrics at the top of the dashboard:

- **Total Emails**: Total number of emails in MongoDB
- **Shown Emails**: Number of emails displayed based on current filters
- **Avg. Confidence**: Average classification confidence score across all emails
- **High Confidence Emails**: Count of emails with confidence ≥ 80%

### 📈 Classification Distribution

Two interactive charts visualize email classification:

**Bar Chart**: Shows count of emails for each classification label
- Work, Personal, Spam, Promotional, Social, Important

**Pie Chart**: Shows percentage distribution of classifications

Charts are interactive - hover for details, click legend to toggle visibility

### 📬 Email List (Main Feature)

#### Expandable Email View

Each email is displayed as an expandable item showing:

1. **From Address**: Sender's email (truncated for display)
2. **Subject**: Email subject line
3. **Quick Info**: In the header row

Click on an email to expand and view:

#### Detailed Email View

When expanded, each email displays:

**Classification Badge**
- Color-coded badge showing email type
- Green for "WORK"
- Red for "SPAM"  
- Yellow for "PROMOTIONAL"
- Blue for other categories

**Confidence Score**
- Visual progress bar (0-100%)
- Shows classification certainty
- Higher % = more confident classification

**Urgency Level**
- 🔴 Critical: Requires immediate attention
- 🟠 High: Important, should address soon
- 🟡 Normal: Standard importance
- 🟢 Low: Can be addressed later

**5-Second Summary**
- AI-generated brief summary
- Perfect for quick reading without opening full email
- Usually 1-3 sentences of key points

**🏷️ Extracted Information Badges**

Highlighted extracted entities:

- **⏰ Deadline**: Important dates and deadlines
  - Example: "Friday", "2026-04-25", "End of Q1"
  - Red badge for visibility

- **💰 Amount**: Financial figures and amounts
  - Example: "$5000", "€2,500", "1000 units"
  - Teal badge

- **👤 Requester**: Who requested something
  - Example: "John Smith", "Finance Team", "Manager"
  - Yellow badge

- **Other Entities**: Additional extracted information
  - Gray badges for other entity types

Each entity shows extraction confidence level

**Email Details**
- From address (full)
- Date received
- Subject (full)
- Model version used for classification

### 📋 Quick Summary Table

Simplified tabular view of all displayed emails:

| Column | Description |
|--------|-------------|
| From | Sender email address |
| Subject | Email subject line |
| Classification | Email type label |
| Confidence | Classification confidence % |
| Urgency | Urgency level with emoji |
| Date | When email was received |

- Click column headers to sort (if your Streamlit version supports it)
- Shows all filtered emails in compact format

### 📥 Export Options

**Download as CSV**
- Export all displayed emails to CSV format
- Includes: From, Subject, Classification, Confidence, Urgency, Date
- Useful for further analysis or reports

**Excel Export Info**
- Instructions to enable Excel export
- Requires: `pip install openpyxl`

**Detailed Statistics**
- JSON display of statistics
- Total emails, average confidence, classification breakdown

---

## ⚙️ Sidebar Configuration

### Filter by Classification

Dropdown menu to filter emails:
- **All**: Show all classifications
- **work**: Only work-related emails
- **personal**: Only personal emails
- **spam**: Only spam emails
- **promotional**: Only promotional emails
- **social**: Only social emails
- **important**: Only important emails

### Date Range Filter

Slider to show emails from the last N days:
- Minimum: 1 day
- Maximum: 90 days
- Default: 30 days

Useful for:
- Finding recent emails
- Viewing historical data
- Narrowing analysis period

### Number of Emails to Display

Slider to control how many emails to show:
- Minimum: 10 emails
- Maximum: 500 emails
- Default: 50 emails

**Note**: More emails = slower loading time

### Auto-refresh Interval

Dropdown to set automatic refresh frequency:
- **Manual**: No automatic refresh (default)
- **5 seconds**: Refresh every 5 seconds
- **30 seconds**: Refresh every 30 seconds
- **1 minute**: Refresh every 60 seconds
- **5 minutes**: Refresh every 300 seconds

Perfect for monitoring emails in real-time

### Refresh Button

Manual refresh button to immediately fetch latest data:
- Green button "🔄 Refresh Data"
- Fetches new emails from MongoDB
- Updates all statistics and charts

---

## 🔍 Usage Examples

### Example 1: Finding Urgent Emails

1. In sidebar, select **Classification**: "work"
2. Set **Date Range**: 7 days
3. Click **Expand** on emails
4. Look for 🔴 Red urgency badges
5. Read the 5-second **Summary**
6. Check extracted **Deadlines**

### Example 2: Analyzing Classification Confidence

1. View the **Avg. Confidence** metric (top)
2. Look at **Classification Distribution** pie chart
3. For each email, check the **Confidence Score** progress bar
4. Filter low-confidence emails for review
5. Adjust AI model if confidence consistently low

### Example 3: Extracting Financial Information

1. Set **Classification**: "work"
2. Expand each email
3. Look for 💰 **Amount badges** in extracted info
4. Review all financial figures mentioned
5. **Export as CSV** for spreadsheet analysis

### Example 4: Monitoring Real-time Emails

1. Set **Auto-refresh**: "5 seconds"
2. Set **Classification**: "All"
3. Set **Emails to display**: 20 (smaller number = faster refresh)
4. Watch dashboard update automatically
5. System monitors for new incoming emails

### Example 5: Report Generation

1. Filter emails by date, classification, etc.
2. Click **📥 Download as CSV**
3. Open in Excel or Google Sheets
4. Create charts and reports
5. Send to stakeholders

---

## 🐛 Troubleshooting

### Issue: Dashboard won't load

**Error**: Connection refused or "Can't reach MongoDB"

**Solutions**:
```bash
# Check MongoDB is running
docker-compose ps

# Start MongoDB
docker-compose up -d mongodb

# Check MongoDB logs
docker-compose logs mongodb

# Test MongoDB connection
mongosh mongodb://admin:changeme123@localhost:27017
```

### Issue: No emails showing

**Possible causes**:
1. MongoDB empty (no emails have been classified yet)
2. Date range filter too narrow
3. Classification filter too specific

**Solutions**:
- Run the test script to add sample emails:
  ```bash
  python scripts/test_mongodb_api.py
  ```
- Increase "Show emails from last (days)" to 90
- Set classification filter to "All"

### Issue: Dashboard is slow

**Causes**:
- Too many emails displayed
- MongoDB indexes missing
- Network latency

**Solutions**:
- Reduce "Number of emails to display" to 20-50
- Check MongoDB indexes:
  ```bash
  mongosh mongodb://admin:changeme123@localhost:27017
  use email_classifier
  db.classified_emails.getIndexes()
  ```
- Increase "Show emails from last (days)" to show fewer results

### Issue: "Port 8501 already in use"

**Solution**:
```bash
# Use different port
streamlit run streamlit_dashboard.py --server.port 8502
```

### Issue: Charts not displaying

**Solution**:
```bash
# Reinstall plotly
pip install --upgrade plotly
```

---

## 🔧 Advanced Configuration

### Custom MongoDB Connection

Edit the dashboard file to change MongoDB connection:

```python
# In streamlit_dashboard.py, change these lines:
MONGODB_URL = "your-mongodb-url"
MONGODB_DB_NAME = "your-database-name"
```

Or use environment variables in `.env`:
```bash
MONGODB_URL=mongodb://admin:password@host:27017
MONGODB_DB_NAME=email_classifier
```

### Customize Appearance

Streamlit dashboard style can be customized via `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#FF6B6B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
```

### Increase Session Timeout

```bash
# Run with custom timeout (in seconds)
streamlit run streamlit_dashboard.py --client.sessionState.timeout 3600
```

---

## 📊 Data Insights You Can Gain

### Classification Accuracy

- Compare "Avg. Confidence" metric
- Check distribution chart
- Find low-confidence emails for review

### Email Volume Trends

- Monitor total email count over time
- Identify peak email periods
- Track classification distribution changes

### Entity Extraction Quality

- Review deadline extraction accuracy
- Check amount detection in financial emails
- Validate requester identification

### Urgency Pattern Analysis

- Count emails by urgency level
- Identify most urgent email types
- Plan workload accordingly

### Sender Analysis

- Filter by sender domain
- Identify most frequent senders
- Check classification patterns per sender

---

## 💡 Tips & Best Practices

### 1. Regular Monitoring
- Set auto-refresh to 30 seconds
- Monitor throughout the day
- Catch urgent emails early

### 2. Weekly Analysis
- Export weekly CSV report
- Analyze trends
- Identify patterns

### 3. Model Improvement
- Note low-confidence classifications
- Collect feedback data
- Retrain model periodically

### 4. Team Collaboration
- Share CSV exports with team
- Use dashboard for status meetings
- Create automated reports

### 5. Performance Optimization
- Keep displayed emails ≤ 100
- Filter by date range (1-7 days)
- Refresh every 30-60 seconds max

---

## 🚀 Integration with FastAPI

The dashboard reads from the same MongoDB database as the FastAPI backend:

1. **Email Classification**: FastAPI endpoint saves to MongoDB
2. **Dashboard Display**: Streamlit reads from MongoDB
3. **Real-time Sync**: Both see same data immediately

Workflow:
```
Gmail Email
   ↓
FastAPI Endpoint
   ↓
AI Classification
   ↓
MongoDB Save
   ↓
Streamlit Dashboard (reads)
```

---

## 📚 Related Documentation

- [Streamlit Official Docs](https://docs.streamlit.io/)
- [MongoDB Python Driver](https://docs.mongodb.com/drivers/pymongo/)
- [Plotly Visualization](https://plotly.com/python/)
- [Pandas DataFrame](https://pandas.pydata.org/docs/)
- [Motor Async Driver](https://motor.readthedocs.io/)

---

## 🎯 Next Steps

After setting up the dashboard:

1. ✅ Run sample data through FastAPI classifier
2. ✅ View results in dashboard
3. ✅ Export CSV reports
4. ✅ Monitor key metrics
5. ✅ Iterate on AI model based on results
6. ✅ Deploy to production

---

## 📞 Support

**Issue**: Dashboard crashes when opening
**Solution**: Check browser console (F12) for errors, refresh page

**Issue**: Some emails have no summary
**Solution**: These emails weren't processed by summarizer, check FastAPI logs

**Issue**: Extracted entities empty
**Solution**: Email body might be too short or in unsupported language

---

**Dashboard Version**: 1.0.0  
**Last Updated**: 2026-04-18  
**Compatible with**: Streamlit 1.28+, MongoDB 7.0+, Python 3.8+
