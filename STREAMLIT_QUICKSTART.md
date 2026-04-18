# Quick Start - Streamlit Email Dashboard

## 🎯 30-Second Setup

```bash
# 1. Install dependencies
pip install streamlit plotly pandas

# 2. Start MongoDB (if using Docker)
docker-compose up -d mongodb

# 3. Run dashboard
streamlit run streamlit_dashboard.py
```

Dashboard opens at: **http://localhost:8501**

---

## 📊 What You'll See

### 1. Overview Statistics
- Total emails in database
- Average classification confidence
- High-confidence email count

### 2. Classification Charts
- Bar chart: Email count by type
- Pie chart: Classification distribution

### 3. Email List
- Expandable email entries
- Each shows:
  - **📝 5-Second Summary** (AI-generated)
  - **🏷️ Extracted Information** (Deadlines, Amounts, Requesters)
  - **🎯 Classification** with confidence score
  - **🚨 Urgency Level** (Critical/High/Normal/Low)

### 4. Quick Summary Table
- Compact table view of all emails
- Sortable columns

---

## ⚙️ Configuration (Left Sidebar)

| Setting | Purpose |
|---------|---------|
| Filter by Classification | Show specific email types |
| Show emails from last | Date range (1-90 days) |
| Number of emails | How many to display (10-500) |
| Auto-refresh interval | Real-time monitoring (5s-5m) |
| Refresh Data button | Manual refresh |

---

## 🎨 Color Coding

### Classification Badges
- 🟢 Green: Work emails
- 🔴 Red: Spam emails
- 🟡 Yellow: Promotional
- 🔵 Blue: Other

### Urgency Levels
- 🔴 Critical: Red (highest)
- 🟠 High: Orange
- 🟡 Normal: Yellow
- 🟢 Low: Green (lowest)

### Extracted Entities
- **⏰ Deadline**: Red badge
- **💰 Amount**: Teal badge
- **👤 Requester**: Yellow badge

---

## 📥 Export Data

Click **📥 Download as CSV** to:
- Export all displayed emails
- Create reports in Excel
- Share with team

---

## 🚨 Common Issues

| Issue | Fix |
|-------|-----|
| "Can't reach MongoDB" | Run `docker-compose up -d mongodb` |
| No emails showing | Increase date range to 90 days |
| Dashboard slow | Reduce email count to 20-50 |
| Port 8501 in use | Use `--server.port 8502` |

---

## 🔄 Sample Data

To test with sample emails:

```bash
# Run test script to populate MongoDB
python scripts/test_mongodb_api.py
```

Then refresh dashboard to see emails!

---

## 📚 Full Guide

See **STREAMLIT_DASHBOARD_GUIDE.md** for:
- Complete feature documentation
- Advanced configuration
- Troubleshooting guide
- Usage examples
- Integration details

---

## 🎯 Use Cases

**Real-time Monitoring**
- Set auto-refresh to 5 seconds
- Monitor incoming emails
- Catch urgent items immediately

**Weekly Reports**
- Filter by date range
- Export as CSV
- Create summary reports

**Quality Assurance**
- Check classification accuracy
- Review low-confidence emails
- Identify model improvements

**Team Dashboard**
- Display on office screen
- Show email volume trends
- Monitor system health

---

## 💡 Pro Tips

1. **Fastest Loading**: Show 20-30 emails, last 7 days
2. **Best Monitoring**: Auto-refresh every 30 seconds
3. **Weekly Reports**: Export Friday EOD data
4. **Model Improvement**: Flag emails with <0.7 confidence
5. **Mobile Viewing**: Works on tablets/phones in responsive mode

---

**Ready to start?** Run: `streamlit run streamlit_dashboard.py`
