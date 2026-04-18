# MongoDB + FastAPI 使用示例指南
## 实际测试和使用代码片段

---

## 📋 目录

1. [cURL 命令示例](#curl-命令示例)
2. [Python 测试脚本](#python-测试脚本)
3. [常见用例](#常见用例)
4. [故障排除](#故障排除)

---

## cURL 命令示例

### 1️⃣ 分类和保存邮件

```bash
# 保存一封"工作"分类的邮件
curl -X POST "http://localhost:8000/api/v1/emails/classify-and-save" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg_001",
    "thread_id": "thread_001",
    "subject": "Q1 2026 Budget Review",
    "from_email": "boss@company.com",
    "to_emails": ["you@company.com"],
    "body": "Dear Team, please review the Q1 2026 budget proposal and provide feedback by Friday. The deadline for submission is April 25th.",
    "received_date": "2026-04-18T10:30:00Z",
    "gmail_labels": ["INBOX", "STARRED"]
  }'

# 预期响应:
# {
#   "status": "success",
#   "message": "邮件已分类并保存",
#   "document_id": "msg_001",
#   "classification": "work",
#   "confidence_score": 0.92,
#   "summary": "Q1 2026 Budget Review"
# }
```

### 2️⃣ 获取单个邮件

```bash
# 获取已保存的邮件详情
curl -X GET "http://localhost:8000/api/v1/emails/msg_001" \
  -H "Content-Type: application/json"

# 预期响应包含完整的邮件信息
# 包括: 分类标签、置信度、摘要、提取的实体、情感分析等
```

### 3️⃣ 按分类标签查询

```bash
# 获取所有"工作"分类的邮件（分页）
curl -X GET "http://localhost:8000/api/v1/emails/label/work?limit=50&skip=0"

# 获取"个人"分类的邮件
curl -X GET "http://localhost:8000/api/v1/emails/label/personal?limit=50&skip=0"

# 获取"垃圾邮件"
curl -X GET "http://localhost:8000/api/v1/emails/label/spam?limit=100&skip=0"
```

### 4️⃣ 按发件人查询

```bash
# 获取来自特定发件人的所有邮件
curl -X GET "http://localhost:8000/api/v1/emails/sender/boss@company.com?limit=50&skip=0"

# URL 编码发件人邮箱（如果包含特殊字符）
curl -X GET "http://localhost:8000/api/v1/emails/sender/john%2Bdoe@gmail.com"
```

### 5️⃣ 高级搜索

```bash
# 查询来自特定发件人且置信度 >= 0.8 的工作邮件
curl -X POST "http://localhost:8000/api/v1/emails/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "classification_label": "work",
      "sender": "boss@company.com",
      "confidence_score": {"$gte": 0.8}
    },
    "limit": 50,
    "skip": 0,
    "sort_by": "created_at",
    "sort_order": -1
  }'

# 查询最近 7 天内的紧急邮件
curl -X POST "http://localhost:8000/api/v1/emails/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "created_at": {"$gte": "2026-04-11T00:00:00Z"},
      "sentiment_analysis.urgency_level": {"$in": ["high", "critical"]}
    },
    "limit": 100
  }'
```

### 6️⃣ 获取统计信息

```bash
# 获取邮件分类统计
curl -X GET "http://localhost:8000/api/v1/stats"

# 预期响应:
# {
#   "status": "success",
#   "timestamp": "2026-04-18T15:30:45.123456Z",
#   "statistics": {
#     "total_emails": 450,
#     "by_classification": {
#       "work": 150,
#       "personal": 120,
#       "spam": 45,
#       "promotional": 80,
#       "social": 55
#     }
#   }
# }
```

### 7️⃣ 健康检查

```bash
# 检查 API 健康状态
curl -X GET "http://localhost:8000/api/v1/health"

# 预期响应:
# {
#   "status": "healthy",
#   "timestamp": "2026-04-18T15:30:45Z",
#   "services": {
#     "api": "running",
#     "mongodb": "connected",
#     "redis": "connected"
#   }
# }
```

---

## Python 测试脚本

### 完整测试套件

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB + FastAPI 完整测试脚本
使用 requests 库进行 HTTP 测试
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# 配置
API_BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response: requests.Response):
    """美化打印响应"""
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)

# ==================== 测试用例 ====================

def test_1_save_email():
    """测试 1: 保存分类邮件"""
    print_section("测试 1: 保存分类邮件")
    
    email_data = {
        "message_id": f"msg_{datetime.now().timestamp()}",
        "thread_id": "thread_001",
        "subject": "Q1 Budget Review Meeting",
        "from_email": "boss@company.com",
        "to_emails": ["you@company.com"],
        "body": "Dear Team, we need to finalize the Q1 budget by Friday. Please send your proposals and estimated amounts. The deadline is April 25, 2026. Contact: John Doe",
        "received_date": datetime.utcnow().isoformat() + "Z",
        "gmail_labels": ["INBOX", "STARRED"]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/emails/classify-and-save",
        json=email_data,
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)
    
    return response.json() if response.status_code == 200 else None

def test_2_get_email(email_id: str):
    """测试 2: 获取单个邮件"""
    print_section(f"测试 2: 获取邮件 - {email_id}")
    
    response = requests.get(
        f"{API_BASE_URL}/emails/{email_id}",
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_3_query_by_label():
    """测试 3: 按分类标签查询"""
    print_section("测试 3: 按分类标签查询")
    
    params = {
        "limit": 10,
        "skip": 0
    }
    
    response = requests.get(
        f"{API_BASE_URL}/emails/label/work",
        params=params,
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_4_query_by_sender():
    """测试 4: 按发件人查询"""
    print_section("测试 4: 按发件人查询")
    
    params = {
        "limit": 10,
        "skip": 0
    }
    
    response = requests.get(
        f"{API_BASE_URL}/emails/sender/boss@company.com",
        params=params,
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_5_advanced_search():
    """测试 5: 高级搜索"""
    print_section("测试 5: 高级搜索")
    
    # 查询条件: 工作邮件 + 高置信度 + 最近 7 天
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    search_query = {
        "query": {
            "classification_label": "work",
            "confidence_score": {"$gte": 0.8},
            "created_at": {"$gte": week_ago}
        },
        "limit": 50,
        "skip": 0,
        "sort_by": "created_at",
        "sort_order": -1
    }
    
    response = requests.post(
        f"{API_BASE_URL}/emails/search",
        json=search_query,
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_6_statistics():
    """测试 6: 获取统计信息"""
    print_section("测试 6: 获取统计信息")
    
    response = requests.get(
        f"{API_BASE_URL}/stats",
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_7_health_check():
    """测试 7: 健康检查"""
    print_section("测试 7: 健康检查")
    
    response = requests.get(
        f"{API_BASE_URL}/health",
        headers=HEADERS
    )
    
    print(f"状态码: {response.status_code}")
    print_response(response)

def test_bulk_save():
    """批量保存邮件（压力测试）"""
    print_section("批量保存邮件 (20 封)")
    
    subjects = [
        "Q1 Budget Review",
        "Team Meeting Tomorrow",
        "Project Update Required",
        "Client Feedback",
        "System Alert"
    ]
    
    senders = [
        "boss@company.com",
        "colleague@company.com",
        "client@external.com",
        "system@alerts.com"
    ]
    
    success_count = 0
    
    for i in range(20):
        email_data = {
            "message_id": f"bulk_msg_{i}_{int(datetime.now().timestamp())}",
            "thread_id": f"thread_{i}",
            "subject": f"{subjects[i % len(subjects)]} #{i}",
            "from_email": senders[i % len(senders)],
            "to_emails": ["you@company.com"],
            "body": f"This is test email number {i}. {subjects[i % len(subjects)]}",
            "received_date": datetime.utcnow().isoformat() + "Z",
            "gmail_labels": ["INBOX"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/emails/classify-and-save",
            json=email_data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            success_count += 1
            print(f"✅ 邮件 {i+1}/20 - 保存成功")
        else:
            print(f"❌ 邮件 {i+1}/20 - 保存失败: {response.status_code}")
    
    print(f"\n📊 总结: {success_count}/20 邮件保存成功")

# ==================== 主执行 ====================

def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始 MongoDB + FastAPI 测试套件")
    print(f"API 地址: {API_BASE_URL}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试 1: 保存邮件
        result = test_1_save_email()
        
        if result and result.get("status") == "success":
            email_id = result.get("document_id")
            
            # 测试 2: 获取邮件
            test_2_get_email(email_id)
        
        # 测试 3-7: 其他测试
        test_3_query_by_label()
        test_4_query_by_sender()
        test_5_advanced_search()
        test_6_statistics()
        test_7_health_check()
        
        # 批量测试
        test_bulk_save()
        
        print_section("✅ 所有测试完成")
        
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到 API 服务")
        print("请确保 FastAPI 应用正在运行: python src/main.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    # 运行所有测试
    run_all_tests()
    
    # 或者运行单个测试
    # test_7_health_check()
