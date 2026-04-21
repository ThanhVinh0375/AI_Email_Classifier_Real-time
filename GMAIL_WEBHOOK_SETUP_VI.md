# 🚀 Hướng Dẫn Thiết Lập Gmail Webhook

## Tổng Quan
Hướng dẫn này sẽ giúp bạn thiết lập Gmail webhook để tự động nhận và phân loại email thật.

## 📋 Điều Kiện Tiên Quyết

### 1. Tài Khoản Google Cloud
- Tài khoản Google Cloud Platform (GCP)
- Billing enabled (có thể dùng free tier)

### 2. Gmail Account
- Tài khoản Gmail để test
- Gmail API enabled

### 3. API Keys
- OpenAI API key (cho LLM analysis)

---

## 🔧 Các Bước Thiết Lập

### Bước 1: Tạo Google Cloud Project

1. Vào [Google Cloud Console](https://console.cloud.google.com)
2. Tạo project mới hoặc chọn project existing
3. Ghi nhớ **Project ID** (ví dụ: `my-email-classifier-123456`)

### Bước 2: Enable Gmail API

1. Trong Google Cloud Console, vào **APIs & Services** → **Enable APIs and Services**
2. Tìm kiếm **Gmail API**
3. Click **Enable**

### Bước 3: Tạo Service Account

1. Vào **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Điền thông tin:
   - **Name**: `email-classifier-service`
   - **Description**: `Service account for Gmail email classification`
4. Click **Create and Continue**
5. **Role**: Chọn **Editor** (hoặc tạo custom role với Gmail và Pub/Sub permissions)
6. Click **Done**

### Bước 4: Tạo JSON Key

1. Trong Service Accounts, click vào service account vừa tạo
2. Vào tab **Keys**
3. Click **Add Key** → **Create new key** → **JSON**
4. Download file JSON
5. Lưu vào: `credentials/service-account-key.json`

### Bước 5: Cập Nhật File .env

Mở file `.env` và cập nhật các giá trị:

```env
# Thay thế bằng Project ID thật
GCP_PROJECT_ID=your-actual-project-id

# Đường dẫn đến file credentials
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json

# Pub/Sub topic (full path)
GCP_PUBSUB_TOPIC=projects/your-actual-project-id/topics/gmail-notifications

# OpenAI API key thật
LLM_API_KEY=sk-your-actual-openai-key
```

### Bước 6: Cài Đặt gcloud CLI (nếu chưa có)

```bash
# Download và cài đặt Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Bước 7: Tạo Pub/Sub Resources

```bash
# Tạo topic
gcloud pubsub topics create gmail-notifications

# Tạo subscription (cho local development)
gcloud pubsub subscriptions create gmail-notifications-sub \
  --topic=gmail-notifications \
  --push-endpoint=http://localhost:8000/api/v1/webhook/gmail
```

### Bước 8: Chạy Setup Script

```bash
# Chạy helper script
python scripts/setup_webhook_helper.py
```

### Bước 9: Khởi Động Services

```bash
# Start tất cả services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

---

## 🧪 Test Hệ Thống

### Gửi Email Test

1. Gửi email đến tài khoản Gmail của bạn
2. Chờ vài giây để xử lý
3. Kiểm tra dashboard: `streamlit run streamlit_dashboard.py`

### Kiểm Tra Logs

```bash
# Xem logs API
docker-compose logs -f api

# Xem logs MongoDB
docker-compose logs -f mongodb
```

---

## 🔧 Troubleshooting

### Lỗi "Credentials not found"
- Đảm bảo file `credentials/service-account-key.json` tồn tại
- Kiểm tra đường dẫn trong `.env`

### Lỗi "Pub/Sub topic not found"
```bash
# Tạo lại topic
gcloud pubsub topics create gmail-notifications
```

### Lỗi "Gmail API not enabled"
- Vào Google Cloud Console → APIs & Services
- Enable Gmail API

### Webhook không nhận được email
- Kiểm tra webhook URL trong subscription
- Đảm bảo FastAPI server đang chạy
- Check logs: `docker-compose logs api`

---

## 📝 Lưu Ý Quan Trọng

### Cho Production
- Sử dụng HTTPS webhook URL (không phải localhost)
- Cấu hình authentication cho webhook
- Monitor usage và costs

### Security
- Không commit file credentials vào Git
- Sử dụng environment variables cho sensitive data
- Rotate service account keys regularly

---

## 🎯 Kết Luận

Sau khi hoàn thành setup, hệ thống sẽ:
1. ✅ Tự động nhận email mới từ Gmail
2. ✅ Phân loại email bằng Hybrid AI
3. ✅ Lưu kết quả vào MongoDB
4. ✅ Hiển thị trên Streamlit dashboard

Chúc bạn thành công! 🚀