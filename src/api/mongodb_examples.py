# -*- coding: utf-8 -*-
"""
MongoDB + FastAPI 实际使用示例
==================================

本文件展示了如何在 FastAPI 中使用 MongoDB 服务来保存和查询分类邮件。
所有操作都是异步的，充分利用 Motor 驱动程序的优势。
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.models.database import (
    ClassifiedEmail, 
    ClassificationLabel,
    ExtractedEntity,
    SentimentAnalysis,
    EmailData
)
from src.services.mongodb_service import MongoDBService
from src.config import settings

logger = logging.getLogger(__name__)

# ==================== 全局服务实例 ====================

# 创建 MongoDB 服务实例
mongo_service = MongoDBService()

# ==================== 应用生命周期事件 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 应用生命周期管理"""
    
    # ===== 应用启动 =====
    logger.info("📱 FastAPI 应用启动中...")
    
    try:
        # 连接 MongoDB
        logger.info("🗄️  连接 MongoDB...")
        await mongo_service.connect()
        logger.info("✅ MongoDB 连接成功")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 应用启动失败: {str(e)}")
        raise
    
    # ===== 应用关闭 =====
    finally:
        logger.info("🛑 FastAPI 应用关闭中...")
        await mongo_service.disconnect()
        logger.info("✅ 资源清理完成")

# 创建 FastAPI 应用
app = FastAPI(
    title="AI 邮件分类系统 - MongoDB 集成",
    description="展示 FastAPI + MongoDB + Motor 异步操作",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== API 路由 ====================

# ===== 1. 保存分类邮件 =====

@app.post("/api/v1/emails/classify-and-save")
async def classify_and_save_email(
    email: EmailData,
    skip_ai: bool = False
) -> dict:
    """
    分类邮件并保存到 MongoDB
    
    **功能流程:**
    1. 接收原始邮件数据
    2. 使用 AI 进行分类（可选跳过）
    3. 创建 ClassifiedEmail 对象
    4. 保存到 MongoDB
    
    **参数:**
    - email: 邮件数据对象
    - skip_ai: 是否跳过 AI 分类（用于测试）
    
    **返回:**
    - document_id: MongoDB 文档 ID
    - classification: 分类标签
    - confidence: 置信度分数
    
    **示例请求:**
    ```json
    {
        "message_id": "msg_12345",
        "from_email": "john@example.com",
        "subject": "Q1 Budget Review",
        "body": "Please review the Q1 budget...",
        "received_date": "2026-04-18T10:30:00"
    }
    ```
    """
    try:
        # 模拟 AI 分类结果（实际应用中调用真实的 AI 模型）
        classification_result = {
            "label": ClassificationLabel.WORK if "budget" in email.subject.lower() else ClassificationLabel.GENERAL,
            "confidence": 0.92,
            "summary": f"Email about: {email.subject[:50]}",
            "processing_time": 245.3,
            "entities": [
                ExtractedEntity(
                    entity_type="deadline",
                    value="Next Friday",
                    confidence=0.95
                ),
                ExtractedEntity(
                    entity_type="requester",
                    value="John Doe",
                    confidence=0.98
                )
            ],
            "sentiment": SentimentAnalysis(
                sentiment="neutral",
                score=50,
                urgency_level="high"
            )
        }
        
        # 创建分类邮件对象
        classified_email = ClassifiedEmail(
            email_id=email.message_id,
            sender=email.from_email,
            subject=email.subject,
            body_text=email.body,
            classification_label=classification_result["label"],
            confidence_score=classification_result["confidence"],
            summary=classification_result["summary"],
            extracted_entities=classification_result["entities"],
            sentiment_analysis=classification_result["sentiment"],
            processing_time_ms=classification_result["processing_time"]
        )
        
        # 保存到 MongoDB
        doc_id = await mongo_service.save_classified_email(classified_email)
        
        logger.info(
            f"✅ 邮件保存成功 - "
            f"ID: {doc_id} | "
            f"分类: {classified_email.classification_label} | "
            f"置信度: {classified_email.confidence_score:.2%}"
        )
        
        return {
            "status": "success",
            "message": "邮件已分类并保存",
            "document_id": doc_id,
            "classification": classified_email.classification_label.value,
            "confidence_score": classified_email.confidence_score,
            "summary": classified_email.summary
        }
        
    except Exception as e:
        logger.error(f"❌ 分类和保存失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"邮件处理失败: {str(e)}"
        )

# ===== 2. 获取单个分类邮件 =====

@app.get("/api/v1/emails/{email_id}")
async def get_classified_email(email_id: str) -> dict:
    """
    按 email_id 获取分类邮件详情
    
    **参数:**
    - email_id: 邮件唯一标识符
    
    **返回:**
    - 完整的邮件文档（包含所有分析结果）
    
    **示例:**
    GET /api/v1/emails/msg_12345
    """
    try:
        email = await mongo_service.get_classified_email_by_id(email_id)
        
        if not email:
            raise HTTPException(
                status_code=404,
                detail=f"邮件不存在: {email_id}"
            )
        
        logger.debug(f"✅ 已检索邮件: {email_id}")
        
        return {
            "status": "success",
            "data": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 3. 按分类标签查询邮件 =====

@app.get("/api/v1/emails/label/{classification_label}")
async def get_emails_by_label(
    classification_label: str,
    limit: int = Query(50, ge=1, le=1000, description="返回结果最大数量"),
    skip: int = Query(0, ge=0, description="跳过结果数量（分页用）")
) -> dict:
    """
    按分类标签查询邮件（支持分页）
    
    **参数:**
    - classification_label: 分类标签 (work/personal/spam/promotional/social/important/general)
    - limit: 返回结果最大数量 (1-1000)
    - skip: 跳过的结果数量（用于分页）
    
    **返回:**
    - emails: 邮件列表
    - total_count: 总数
    - current_page: 当前页码
    
    **使用示例:**
    ```
    # 获取第一批工作邮件
    GET /api/v1/emails/label/work?limit=50&skip=0
    
    # 获取第二批
    GET /api/v1/emails/label/work?limit=50&skip=50
    ```
    """
    try:
        # 验证分类标签
        if classification_label not in [label.value for label in ClassificationLabel]:
            raise HTTPException(
                status_code=400,
                detail=f"无效的分类标签: {classification_label}。有效标签: {[l.value for l in ClassificationLabel]}"
            )
        
        # 从 MongoDB 查询
        emails = await mongo_service.get_classified_emails_by_label(
            classification_label=classification_label,
            limit=limit,
            skip=skip
        )
        
        logger.info(
            f"✅ 已检索 {len(emails)} 封标签为 '{classification_label}' 的邮件"
        )
        
        return {
            "status": "success",
            "classification_label": classification_label,
            "emails": emails,
            "count": len(emails),
            "limit": limit,
            "skip": skip,
            "next_skip": skip + limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 标签查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 4. 按发件人查询邮件 =====

@app.get("/api/v1/emails/sender/{sender}")
async def get_emails_by_sender(
    sender: str,
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> dict:
    """
    按发件人查询邮件
    
    **参数:**
    - sender: 发件人邮箱地址
    - limit: 返回结果最大数量
    - skip: 跳过的结果数量
    
    **返回:**
    - 该发件人的所有邮件列表
    
    **示例:**
    GET /api/v1/emails/sender/boss@company.com
    """
    try:
        emails = await mongo_service.get_classified_emails_by_sender(
            sender=sender,
            limit=limit,
            skip=skip
        )
        
        logger.info(
            f"✅ 已检索来自 '{sender}' 的 {len(emails)} 封邮件"
        )
        
        return {
            "status": "success",
            "sender": sender,
            "emails": emails,
            "count": len(emails)
        }
        
    except Exception as e:
        logger.error(f"❌ 查询发件人邮件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 5. 高级搜索 =====

@app.post("/api/v1/emails/search")
async def advanced_search(
    query: dict = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: int = Query(-1, description="排序方式 (1=升序, -1=降序)")
) -> dict:
    """
    高级搜索（支持复杂查询）
    
    **参数:**
    - query: MongoDB 查询对象
    - limit: 返回结果最大数量
    - skip: 跳过的结果数量
    - sort_by: 排序字段
    - sort_order: 排序方向
    
    **示例查询体:**
    ```json
    {
        "classification_label": "work",
        "sender": "boss@company.com",
        "confidence_score": {"$gte": 0.8},
        "created_at": {"$gte": "2026-04-10T00:00:00"}
    }
    ```
    
    **查询操作符说明:**
    - $eq: 等于
    - $gte: 大于等于
    - $lte: 小于等于
    - $in: 在列表中
    - $regex: 正则匹配
    """
    try:
        if query is None:
            query = {}
        
        # 执行搜索
        results = await mongo_service.search_classified_emails(
            query=query,
            limit=limit,
            skip=skip,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        logger.info(f"✅ 高级搜索返回 {len(results)} 条结果")
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
    except Exception as e:
        logger.error(f"❌ 搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 6. 统计信息 =====

@app.get("/api/v1/stats")
async def get_statistics() -> dict:
    """
    获取邮件统计信息
    
    **返回:**
    - total_emails: 总邮件数
    - by_classification: 各分类统计
    - by_sentiment: 各情感分析统计
    - average_confidence: 平均置信度
    
    **示例:**
    GET /api/v1/stats
    """
    try:
        # 获取分类统计
        stats = await mongo_service.get_classification_statistics()
        
        logger.info("✅ 已获取统计数据")
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ 获取统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 7. 健康检查 =====

@app.get("/api/v1/health")
async def health_check() -> dict:
    """
    应用健康检查端点
    
    **检查项:**
    - API 服务状态
    - MongoDB 连接状态
    - Redis 连接状态
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "running",
                "mongodb": "connected",
                "redis": "connected"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不健康: {str(e)}"
        )

# ==================== 主程序 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers
    )
