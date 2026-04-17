#!/usr/bin/env python3
"""
Demo script for Hybrid Email Classification

Shows how to use the Hybrid AI classifier with:
1. Spam detection (TF-IDF + Naive Bayes)
2. Deep LLM analysis (Summarization, NER, Sentiment)

Usage: python scripts/demo_hybrid_classifier.py
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.spam_detector import SpamDetector, get_spam_detector
from src.models.hybrid_classifier import get_hybrid_classifier
from src.utils import get_logger

logger = get_logger(__name__)

# Test emails
DEMO_EMAILS = [
    {
        "name": "Spam Email",
        "subject": "URGENT: Claim Your FREE $10000 NOW!!!",
        "body": """
        Congratulations! You have been selected to receive $10,000 in FREE MONEY!
        Click here NOW to claim your prize before it's too late!
        Limited time offer - act immediately!
        
        Get viagra and cialis at unbelievable prices!
        No credit card required! Risk free trial!
        
        Unsubscribe
        """
    },
    {
        "name": "Important Work Email",
        "subject": "URGENT: Project deadline moved to Friday",
        "body": """
        John,
        
        I need to inform you that the project deadline has been moved up to Friday EOD.
        This is critical for our Q2 delivery.
        
        Can you please review the attached requirements and confirm your team can deliver?
        The client is getting frustrated with delays and this could impact the contract renewal.
        
        Please respond ASAP.
        
        Thanks,
        Sarah
        """
    },
    {
        "name": "Promotional Email",
        "subject": "Special Offer: 50% OFF Everything This Weekend!",
        "body": """
        Don't miss our BIGGEST SALE of the year!
        
        Save 50% on all items this weekend only!
        Free shipping on orders over $50.
        
        Limited stock available - shop now!
        
        Use code: SAVE50 at checkout
        
        Best regards,
        Marketing Team
        """
    },
    {
        "name": "General Work Email",
        "subject": "Team lunch next Friday",
        "body": """
        Hi everyone,
        
        We're planning a team lunch next Friday at 12pm in the conference room.
        Please let me know if you can attend and any dietary restrictions.
        
        Looking forward to catching up!
        
        Thanks,
        Mike
        """
    },
    {
        "name": "Social Email",
        "subject": "Hey! Let's catch up this weekend",
        "body": """
        Hey friend!
        
        I haven't heard from you in a while. How have you been?
        Would love to grab coffee this weekend if you're free.
        
        Let me know what day works best for you.
        
        Talk soon!
        """
    }
]

async def demo_spam_detection():
    """Demo Stage 1: Spam Detection"""
    print("\n" + "="*70)
    print("📧 STAGE 1: SPAM DETECTION (TF-IDF + Naive Bayes)")
    print("="*70)
    
    detector = get_spam_detector()
    
    test_emails = [
        ("URGENT: Claim your FREE money NOW!!! viagra cialis", True),
        ("Team meeting scheduled for tomorrow at 2pm", False),
        ("Limited time: 50% OFF everything!", False),
    ]
    
    for text, expected_spam in test_emails:
        result = detector.predict(text)
        status = "✓" if result['is_spam'] == expected_spam else "✗"
        
        print(f"\n{status} Email: {text[:50]}...")
        print(f"   Is Spam: {result['is_spam']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Probabilities - Spam: {result['probability']['spam']:.2%}, Normal: {result['probability']['normal']:.2%}")

async def demo_hybrid_classification():
    """Demo Stages 1 & 2: Hybrid Classification"""
    print("\n" + "="*70)
    print("🤖 HYBRID CLASSIFICATION (Stage 1 + Stage 2)")
    print("="*70)
    
    classifier = get_hybrid_classifier()
    
    for email in DEMO_EMAILS:
        print(f"\n{'─'*70}")
        print(f"📨 {email['name']}")
        print(f"{'─'*70}")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:100]}...")
        
        # Classify
        result = await classifier.classify({
            'subject': email['subject'],
            'body': email['body']
        })
        
        print(f"\n🎯 Classification Results:")
        print(f"   Class: {result['classification'].upper()}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Processing Time: {result['processing_time_ms']:.0f}ms")
        print(f"   Is Spam: {result.get('is_spam', False)}")
        
        # Show LLM analysis if not spam
        if not result.get('is_spam'):
            llm_analysis = result.get('analysis', {}).get('llm_analysis', {})
            
            if llm_analysis:
                print(f"\n📝 LLM Analysis:")
                
                # Summary
                if 'summary' in llm_analysis:
                    summary = llm_analysis['summary']
                    print(f"   Summary: {summary[:100]}...")
                
                # Sentiment
                if 'sentiment' in llm_analysis:
                    sentiment = llm_analysis['sentiment']
                    print(f"   Sentiment: {sentiment.get('label', 'unknown')} "
                          f"(score: {sentiment.get('score', 0):.2f})")
                    print(f"   Urgent: {sentiment.get('is_urgent', False)}")
                    print(f"   Needs Action: {sentiment.get('requires_immediate_action', False)}")
                
                # Entities
                if 'entities' in llm_analysis:
                    entities = llm_analysis['entities']
                    if entities.get('deadline'):
                        print(f"   Deadline: {entities['deadline']}")
                    if entities.get('requester'):
                        print(f"   Requester: {entities['requester']}")
                    if entities.get('amount'):
                        print(f"   Amount: {entities['amount']}")

async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🎯 HYBRID EMAIL CLASSIFICATION DEMO")
    print("="*70)
    
    # Stage 1 demo
    await demo_spam_detection()
    
    # Hybrid classification demo
    await demo_hybrid_classification()
    
    print("\n" + "="*70)
    print("✅ Demo complete!")
    print("="*70 + "\n")
    
    # Show classifier info
    classifier = get_hybrid_classifier()
    info = classifier.get_spam_detection_features()
    
    print("\n📊 Spam Detection Model Info:")
    print(f"   Top Spam Words: {', '.join(info.get('spam_words', [])[:5])}")
    print(f"   Top Normal Words: {', '.join(info.get('normal_words', [])[:5])}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
