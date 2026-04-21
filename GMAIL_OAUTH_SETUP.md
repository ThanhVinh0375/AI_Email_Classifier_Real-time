# 🚀 GMAIL OAUTH SETUP GUIDE
# ================================

## Vấn đề hiện tại:
Service account không thể trực tiếp truy cập Gmail của bạn.
Cần OAuth 2.0 authentication với user consent.

## Các bước setup:

### 1. Tạo OAuth Client ID
1. Vào Google Cloud Console:
   https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0860833865

2. Click "Create Credentials" → "OAuth 2.0 Client IDs"

3. Chọn Application type: "Desktop application"

4. Download JSON file

### 2. Lưu file credentials
1. Đổi tên file thành: `client_secret.json`
2. Lưu vào thư mục: `./credentials/client_secret.json`

### 3. Chạy setup script
```bash
python scripts/setup_gmail_oauth.py
```

### 4. Authorize access
- Browser sẽ mở để bạn authorize Gmail access
- Chọn tài khoản Gmail muốn monitor
- Grant permissions

## Sau khi setup xong:
- Gmail sẽ gửi notifications khi có email mới
- System sẽ tự động classify emails
- Xem kết quả trên dashboard: http://localhost:8501

## Khởi động hệ thống:
```bash
docker-compose up -d
```