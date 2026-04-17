#!/usr/bin/env python3
"""
Complete Example: Using Hybrid AI Email Classification

This example shows how to integrate and use the hybrid classifier
in a real-world application.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.spam_detector import get_spam_detector
from src.models.llm_analyzer import get_llm_analyzer
from src.models.hybrid_classifier import get_hybrid_classifier
from src.utils import get_logger

logger = get_logger(__name__)

# ============================================================================
# EXAMPLE 1: Stage 1 - Spam Detection Only
# ============================================================================

def example_spam_detection():
    """Example: Quick spam filtering"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Spam Detection (Fast & Free)")
    print("="*70)
    
    detector = get_spam_detector()
    
    emails = [
        {
            'id': '1',
            'subject': 'URGENT: Click here to win $10000!!!',
            'body': 'Congratulations! You are a winner! Click here NOW!'
        },
        {
            'id': '2',
            'subject': 'Team meeting tomorrow',
            'body': 'Hi, we have a team meeting at 2pm tomorrow in the office.'
        },
        {
            'id': '3',
            'subject': 'Special offer: 50% OFF Everything!',
            'body': 'Limited time offer! Buy now and save 50% on all items!'
        }
    ]
    
    print("\n📧 Checking emails for spam...\n")
    
    for email in emails:
        # Combine subject + body for spam detection
        text = f"{email['subject']} {email['body']}"
        
        result = detector.predict(text)
        
        print(f"Email #{email['id']}: {email['subject'][:40]}...")
        print(f"  Is Spam: {result['is_spam']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        
        if result['is_spam']:
            print(f"  → ✓ BLOCKED (Saved API call!)")
        else:
            print(f"  → Continue to Stage 2 for deep analysis")
        print()

# ============================================================================
# EXAMPLE 2: Stage 2 - LLM Analysis for Non-Spam Emails
# ============================================================================

async def example_llm_analysis():
    """Example: Deep email analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 2: LLM Deep Analysis (For Non-Spam Emails)")
    print("="*70)
    
    analyzer = get_llm_analyzer(api_provider="openai")
    
    # Important work email that needs analysis
    email = {
        'subject': 'URGENT: Budget approval needed by EOD Friday',
        'body': '''
        Hi Mike,
        
        The Q2 marketing budget of $150,000 needs your approval by end of business Friday.
        Sarah from accounting has requested confirmation for the quarterly report.
        
        The budget covers:
        - Digital ads: $80,000
        - Content creation: $50,000
        - Events: $20,000
        
        Please respond ASAP as the finance team needs this for their close procedures.
        
        Thanks,
        John
        '''
    }
    
    print(f"\n📧 Analyzing email: {email['subject']}\n")
    
    result = await analyzer.analyze_email(
        subject=email['subject'],
        body=email['body']
    )
    
    print("🔍 LLM Analysis Results:")
    print(f"\n  📝 Summary:")
    print(f"     {result.get('summary', 'N/A')}")
    
    print(f"\n  🏷️  Extracted Entities:")
    entities = result.get('entities', {})
    if entities.get('deadline'):
        print(f"     • Deadline: {entities['deadline']}")
    if entities.get('requester'):
        print(f"     • Requester: {entities['requester']}")
    if entities.get('amount'):
        print(f"     • Amount: {entities['amount']}")
    
    print(f"\n  😊 Sentiment Analysis:")
    sentiment = result.get('sentiment', {})
    print(f"     • Label: {sentiment.get('label', 'unknown')}")
    print(f"     • Score: {sentiment.get('score', 0):.2f} (range: -1 to 1)")
    print(f"     • Urgent: {sentiment.get('is_urgent', False)}")
    print(f"     • Needs Action: {sentiment.get('requires_immediate_action', False)}")
    
    print(f"\n  ⚡ Confidence: {result.get('confidence', 0):.2%}")

# ============================================================================
# EXAMPLE 3: Complete Hybrid Pipeline
# ============================================================================

async def example_hybrid_pipeline():
    """Example: Full hybrid classification"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Complete Hybrid Pipeline")
    print("="*70)
    
    classifier = get_hybrid_classifier()
    
    test_cases = [
        {
            'name': 'Spam Email',
            'subject': 'URGENT!!! Claim Your $1000 FREE!!!',
            'body': 'Buy viagra now! Limited time offer! Click here immediately!'
        },
        {
            'name': 'Important Work Email',
            'subject': 'CRITICAL: Project deadline changed to Friday',
            'body': '''
            The client urgently needs the project delivered by Friday EOD.
            This is critical for the contract renewal.
            Can you confirm your team can deliver?
            '''
        },
        {
            'name': 'Promotional Email',
            'subject': 'Black Friday Sale: 70% OFF Everything!',
            'body': 'Shop now and save 70% on all items! Use code: BF70'
        },
        {
            'name': 'Personal Email',
            'subject': 'Hey! How have you been?',
            'body': 'Hi friend! I miss you. Let\'s catch up this weekend!'
        }
    ]
    
    print("\n🤖 Running hybrid classification on test cases...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test #{i}: {test['name']}")
        print(f"{'─'*70}")
        print(f"Subject: {test['subject']}")
        
        result = await classifier.classify({
            'subject': test['subject'],
            'body': test['body']
        })
        
        print(f"\n✓ Classification: {result['classification'].value.upper()}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Is Spam: {result.get('is_spam', False)}")
        print(f"  Time: {result.get('processing_time_ms', 0):.0f}ms")
        
        # Show why it was classified this way
        if result.get('is_spam'):
            spam_analysis = result.get('analysis', {}).get('spam_analysis', {})
            print(f"\n  Reason: Spam detection (Stage 1)")
            print(f"    Confidence: {spam_analysis.get('confidence', 0):.2%}")
        else:
            llm_analysis = result.get('analysis', {}).get('llm_analysis', {})
            sentiment = llm_analysis.get('sentiment', {})
            
            print(f"\n  Reason: LLM analysis (Stage 2)")
            print(f"    Sentiment: {sentiment.get('label', 'unknown')}")
            print(f"    Urgent: {sentiment.get('is_urgent', False)}")

# ============================================================================
# EXAMPLE 4: Batch Processing
# ============================================================================

async def example_batch_processing():
    """Example: Process multiple emails efficiently"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Processing")
    print("="*70)
    
    classifier = get_hybrid_classifier()
    
    # Simulate batch of 5 emails
    emails = [
        {
            'subject': f'Email {i}: ' + ('SPAM!' if i % 3 == 0 else 'Work'),
            'body': f'This is test email number {i}. ' + 
                    ('Click here for free money!' if i % 3 == 0 else 'Please review attached.')
        }
        for i in range(5)
    ]
    
    print(f"\n📧 Processing batch of {len(emails)} emails...\n")
    
    results = await classifier.classify_batch(emails)
    
    # Summary
    spam_count = sum(1 for r in results if r.get('is_spam', False))
    important_count = sum(1 for r in results 
                         if r['classification'].value == 'important')
    
    print(f"✓ Batch Processing Complete:")
    print(f"  • Total: {len(emails)} emails")
    print(f"  • Spam: {spam_count}")
    print(f"  • Important: {important_count}")
    print(f"  • Processing Method: Hybrid (Fast spam filter + LLM for rest)")

# ============================================================================
# EXAMPLE 5: Cost Analysis
# ============================================================================

def example_cost_analysis():
    """Example: Calculate cost savings"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Cost Analysis & Savings")
    print("="*70)
    
    # Assumptions
    emails_per_day = 100
    spam_percentage = 0.70  # 70% are spam
    gpt35_cost = 0.0015     # per email
    
    spam_count = int(emails_per_day * spam_percentage)
    legit_count = emails_per_day - spam_count
    
    # Pure LLM approach
    pure_llm_cost_daily = emails_per_day * gpt35_cost
    pure_llm_cost_monthly = pure_llm_cost_daily * 30
    
    # Hybrid approach
    # Stage 1 is essentially free (TF-IDF is negligible)
    hybrid_cost_daily = legit_count * gpt35_cost
    hybrid_cost_monthly = hybrid_cost_daily * 30
    
    savings_daily = pure_llm_cost_daily - hybrid_cost_daily
    savings_monthly = pure_llm_cost_monthly - hybrid_cost_monthly
    savings_pct = (savings_monthly / pure_llm_cost_monthly) * 100
    
    print(f"\n💰 Cost Comparison (GPT-3.5-turbo):\n")
    print(f"📊 Assumptions:")
    print(f"   • Emails per day: {emails_per_day}")
    print(f"   • Spam percentage: {spam_percentage:.0%}")
    print(f"   • API cost per email: ${gpt35_cost}")
    
    print(f"\n❌ Pure LLM Approach (Process All):")
    print(f"   • Daily cost: ${pure_llm_cost_daily:.2f}")
    print(f"   • Monthly cost: ${pure_llm_cost_monthly:.2f}")
    
    print(f"\n✅ Hybrid Approach (Spam Filter + LLM):")
    print(f"   • Spam blocked (free): {spam_count} emails")
    print(f"   • LLM processed: {legit_count} emails")
    print(f"   • Daily cost: ${hybrid_cost_daily:.2f}")
    print(f"   • Monthly cost: ${hybrid_cost_monthly:.2f}")
    
    print(f"\n💡 Savings:")
    print(f"   • Daily: ${savings_daily:.2f}")
    print(f"   • Monthly: ${savings_monthly:.2f}")
    print(f"   • Percentage: {savings_pct:.1f}% reduction!")

# ============================================================================
# EXAMPLE 6: Integration with Email Service
# ============================================================================

async def example_integration_with_service():
    """Example: How to integrate with EmailProcessingService"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Integration with Email Service")
    print("="*70)
    
    from src.services.email_service import get_email_processing_service
    
    print(f"\n💻 Integration Points:\n")
    
    service = get_email_processing_service()
    info = service.get_classifier_info()
    
    print(f"📋 Classifier Configuration:")
    for key, value in info.items():
        if key == 'stages':
            print(f"\n   Stages:")
            for stage in value:
                print(f"     • {stage['stage']}: {stage['name']} ({stage['method']})")
        elif key == 'features':
            print(f"\n   Features:")
            for feature in value:
                print(f"     • {feature}")

# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🎯 HYBRID AI EMAIL CLASSIFICATION - COMPLETE EXAMPLES")
    print("="*70)
    
    # Example 1: Spam detection
    example_spam_detection()
    
    # Example 2: LLM analysis
    await example_llm_analysis()
    
    # Example 3: Hybrid pipeline
    await example_hybrid_pipeline()
    
    # Example 4: Batch processing
    await example_batch_processing()
    
    # Example 5: Cost analysis
    example_cost_analysis()
    
    # Example 6: Integration
    await example_integration_with_service()
    
    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70 + "\n")
    
    print("📚 Next Steps:")
    print("   1. Read HYBRID_AI_GUIDE.md for detailed documentation")
    print("   2. Configure your LLM API key in .env")
    print("   3. Run: python scripts/train_spam_detector.py")
    print("   4. Run: python scripts/demo_hybrid_classifier.py")
    print("   5. Deploy with: docker-compose up -d")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExample interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Example error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
