"""
MongoDB Usage Examples for AI Email Classifier

This script demonstrates how to use the async MongoDB service with Motor driver
to save and retrieve classified emails. All operations are fully asynchronous
for maximum performance in real-time email processing pipelines.

Run this script: python scripts/example_mongodb_usage.py
"""

import asyncio
from datetime import datetime, timedelta
from src.services.mongodb_service import MongoDBService
from src.models.database import (
    ClassifiedEmail,
    ClassificationLabel,
    ExtractedEntity,
    SentimentAnalysis
)


# =============================================================================
# EXAMPLE 1: Basic Connection and Save a Classified Email
# =============================================================================

async def example_save_single_email():
    """Save a single classified email to MongoDB"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Save Single Classified Email")
    print("="*80)
    
    # Initialize MongoDB service
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        # Create a sample classified email
        sample_email = ClassifiedEmail(
            email_id="msg_20260417_001",
            sender="john.doe@company.com",
            subject="Q1 Budget Review Meeting - Action Required",
            body_text="""
            Hi team,
            
            We need to complete the Q1 budget review by Friday. Please submit your 
            departmental summaries by Thursday EOD. The review meeting is scheduled 
            for Friday at 2 PM in Conference Room B.
            
            Expected duration: 90 minutes
            Deadline for submissions: Thursday 5 PM
            
            Looking forward to your input.
            
            Best regards,
            John Doe
            Finance Manager
            """,
            classification_label=ClassificationLabel.WORK,
            summary="Q1 budget review meeting scheduled for Friday at 2 PM. Department summaries needed by Thursday 5 PM.",
            extracted_entities=[
                ExtractedEntity(
                    entity_type="deadline",
                    value="Thursday 5 PM",
                    confidence=0.98
                ),
                ExtractedEntity(
                    entity_type="amount",
                    value="Q1 Budget",
                    confidence=0.95
                ),
                ExtractedEntity(
                    entity_type="requester",
                    value="John Doe (Finance Manager)",
                    confidence=0.99
                ),
                ExtractedEntity(
                    entity_type="location",
                    value="Conference Room B",
                    confidence=0.92
                ),
                ExtractedEntity(
                    entity_type="time",
                    value="Friday 2 PM",
                    confidence=0.97
                )
            ],
            sentiment_analysis=SentimentAnalysis(
                sentiment="neutral",
                score=55,
                urgency_level="high"
            ),
            processing_time_ms=234.5,
            confidence_score=0.94
        )
        
        # Save to database
        email_id = await mongo.save_classified_email(sample_email)
        print(f"\n✓ Email saved successfully!")
        print(f"  Email ID: {email_id}")
        print(f"  Classification: {sample_email.classification_label.value}")
        print(f"  Confidence: {sample_email.confidence_score * 100:.1f}%")
        print(f"  Processing Time: {sample_email.processing_time_ms}ms")
        
    except Exception as e:
        print(f"\n✗ Error saving email: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 2: Retrieve Email by ID
# =============================================================================

async def example_get_email_by_id():
    """Retrieve a classified email by ID"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Retrieve Email by ID")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        # Retrieve the email we saved in Example 1
        email_id = "msg_20260417_001"
        email = await mongo.get_classified_email_by_id(email_id)
        
        if email:
            print(f"\n✓ Email found!")
            print(f"  ID: {email.get('email_id')}")
            print(f"  From: {email.get('sender')}")
            print(f"  Subject: {email.get('subject')}")
            print(f"  Classification: {email.get('classification_label')}")
            print(f"  Summary: {email.get('summary')}")
            print(f"  Sentiment: {email.get('sentiment_analysis', {}).get('sentiment')}")
            print(f"  Confidence: {email.get('confidence_score') * 100:.1f}%")
        else:
            print(f"\n✗ Email '{email_id}' not found in database")
            
    except Exception as e:
        print(f"\n✗ Error retrieving email: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 3: Get All Emails from a Specific Sender
# =============================================================================

async def example_get_emails_by_sender():
    """Get all classified emails from a specific sender"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Get Emails from Specific Sender")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        sender = "john.doe@company.com"
        emails = await mongo.get_classified_emails_by_sender(sender, limit=10)
        
        print(f"\n✓ Found {len(emails)} emails from {sender}")
        
        for i, email in enumerate(emails, 1):
            print(f"\n  Email {i}:")
            print(f"    Subject: {email.get('subject')}")
            print(f"    Classification: {email.get('classification_label')}")
            print(f"    Confidence: {email.get('confidence_score') * 100:.1f}%")
            
    except Exception as e:
        print(f"\n✗ Error retrieving emails: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 4: Get Emails by Classification Label
# =============================================================================

async def example_get_emails_by_label():
    """Get all classified emails with a specific label"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Get Emails by Classification Label")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        label = "work"
        emails = await mongo.get_classified_emails_by_label(label, limit=20)
        
        print(f"\n✓ Found {len(emails)} emails with label '{label}'")
        
        # Summary statistics
        avg_confidence = sum(e.get('confidence_score', 0) for e in emails) / len(emails) if emails else 0
        urgency_levels = [e.get('sentiment_analysis', {}).get('urgency_level', 'unknown') for e in emails]
        high_urgency = urgency_levels.count('high') + urgency_levels.count('critical')
        
        print(f"\n  Statistics:")
        print(f"    Total Count: {len(emails)}")
        print(f"    Average Confidence: {avg_confidence * 100:.1f}%")
        print(f"    High/Critical Urgency: {high_urgency}/{len(emails)}")
        
    except Exception as e:
        print(f"\n✗ Error retrieving emails: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 5: Advanced Search with Custom Query
# =============================================================================

async def example_search_classified_emails():
    """Perform flexible searches using MongoDB query syntax"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Advanced Search with Custom Queries")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        # Search 1: High-confidence work emails from the last 7 days
        print("\n  Search 1: High-confidence work emails from last 7 days")
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        high_confidence_work = await mongo.search_classified_emails(
            query={
                "classification_label": "work",
                "confidence_score": {"$gte": 0.90},
                "created_at": {"$gte": week_ago}
            },
            limit=10
        )
        print(f"    ✓ Found {len(high_confidence_work)} high-confidence work emails")
        
        # Search 2: Emails with high urgency from specific sender
        print("\n  Search 2: High urgency emails from john.doe@company.com")
        
        high_urgency_emails = await mongo.search_classified_emails(
            query={
                "sender": "john.doe@company.com",
                "sentiment_analysis.urgency_level": {"$in": ["high", "critical"]}
            },
            limit=10
        )
        print(f"    ✓ Found {len(high_urgency_emails)} high urgency emails")
        
        # Search 3: Personal emails with positive sentiment
        print("\n  Search 3: Personal emails with positive sentiment")
        
        positive_personal = await mongo.search_classified_emails(
            query={
                "classification_label": "personal",
                "sentiment_analysis.sentiment": "positive"
            },
            limit=10
        )
        print(f"    ✓ Found {len(positive_personal)} positive personal emails")
        
    except Exception as e:
        print(f"\n✗ Error during search: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 6: Get Classification Statistics
# =============================================================================

async def example_get_statistics():
    """Get comprehensive statistics about classified emails"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Classification Statistics")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        stats = await mongo.get_classified_email_stats()
        
        print(f"\n✓ Classification Statistics:")
        print(f"  Total Classified Emails: {stats.get('total_classified_emails', 0)}")
        print(f"  Average Processing Time: {stats.get('avg_processing_time_ms', 0):.2f}ms")
        
        print(f"\n  Breakdown by Classification:")
        for label, label_stats in stats.get('by_classification', {}).items():
            print(f"    {label.upper()}: {label_stats['count']} emails (avg confidence: {label_stats['avg_confidence']:.3f})")
        
    except Exception as e:
        print(f"\n✗ Error retrieving statistics: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 7: Bulk Operations - Save Multiple Emails
# =============================================================================

async def example_save_multiple_emails():
    """Save multiple classified emails (batch operation)"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Save Multiple Classified Emails")
    print("="*80)
    
    mongo = MongoDBService()
    await mongo.connect()
    
    try:
        # Create multiple sample emails
        emails_to_save = []
        
        for i in range(3):
            email = ClassifiedEmail(
                email_id=f"msg_20260417_batch_{i+1:03d}",
                sender=f"user{i+1}@company.com",
                subject=f"Sample Email {i+1}: Important Update",
                body_text=f"This is a sample email demonstrating batch operations. Email #{i+1}",
                classification_label=ClassificationLabel.WORK,
                summary=f"Sample email {i+1} for batch processing demonstration",
                extracted_entities=[],
                sentiment_analysis=SentimentAnalysis(
                    sentiment="neutral",
                    score=50,
                    urgency_level="normal"
                ),
                processing_time_ms=100.0 + i * 10,
                confidence_score=0.85 + (i * 0.05)
            )
            emails_to_save.append(email)
        
        # Save all emails concurrently using asyncio.gather
        save_tasks = [mongo.save_classified_email(email) for email in emails_to_save]
        results = await asyncio.gather(*save_tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"\n✓ Batch save completed!")
        print(f"  Successful: {successful}/{len(emails_to_save)}")
        print(f"  Failed: {failed}/{len(emails_to_save)}")
        
        if failed > 0:
            print(f"\n  Errors:")
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"    Email {i+1}: {result}")
        
    except Exception as e:
        print(f"\n✗ Error during batch save: {e}")
    finally:
        await mongo.disconnect()


# =============================================================================
# EXAMPLE 8: Error Handling Best Practices
# =============================================================================

async def example_error_handling():
    """Demonstrate proper error handling with MongoDB operations"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Error Handling Best Practices")
    print("="*80)
    
    mongo = MongoDBService()
    
    try:
        # Simulate connection error handling
        try:
            await mongo.connect()
            print("\n✓ Connected to MongoDB")
        except Exception as e:
            print(f"\n✗ Connection failed: {e}")
            print("  Ensure MongoDB is running and connection string is correct")
            return
        
        # Simulate invalid data error
        try:
            invalid_email = ClassifiedEmail(
                email_id="",  # Empty email_id - should fail validation
                sender="test@example.com",
                subject="Test",
                body_text="Test body",
                classification_label=ClassificationLabel.WORK,
                confidence_score=1.5  # Invalid: should be 0-1
            )
        except Exception as e:
            print(f"\n✓ Validation error caught: {type(e).__name__}")
            print(f"  This demonstrates Pydantic model validation")
        
        # Simulate database operation error recovery
        try:
            email = await mongo.get_classified_email_by_id("nonexistent_email_id")
            if email is None:
                print(f"\n✓ Gracefully handled missing email (returned None)")
            else:
                print(f"  Email found: {email['email_id']}")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
        
    finally:
        try:
            await mongo.disconnect()
            print(f"\n✓ Disconnected from MongoDB")
        except Exception as e:
            print(f"\n✗ Disconnect error: {e}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("AI EMAIL CLASSIFIER - MONGODB USAGE EXAMPLES")
    print("="*80)
    print("\nDemonstrating async MongoDB operations with Motor driver")
    print("All operations are non-blocking and optimized for real-time processing")
    
    # Run examples in sequence
    try:
        await example_save_single_email()
        await example_get_email_by_id()
        await example_get_emails_by_sender()
        await example_get_emails_by_label()
        await example_search_classified_emails()
        await example_get_statistics()
        await example_save_multiple_emails()
        await example_error_handling()
        
        print("\n" + "="*80)
        print("✓ All examples completed successfully!")
        print("="*80)
        print("\nKey Takeaways:")
        print("  1. All operations use async/await for non-blocking I/O")
        print("  2. Motor driver handles connection pooling automatically")
        print("  3. Pydantic models validate data before database operations")
        print("  4. Use search_classified_emails() for flexible MongoDB queries")
        print("  5. Handle exceptions gracefully in production code")
        print("\nFor API usage, see: src/api/emails.py")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Execution interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
