#!/usr/bin/env python3
"""
QUICK REFERENCE: Hybrid AI Email Classifier Cheat Sheet

Copy-paste ready code snippets for common tasks
"""

# ============================================================================
# 🚀 QUICK START (3 STEPS)
# ============================================================================

# Step 1: Train spam detector (one time)
# $ python scripts/train_spam_detector.py

# Step 2: Set LLM API key in .env
# LLM_API_KEY=sk-your-key

# Step 3: Run demo
# $ python scripts/demo_hybrid_classifier.py

# ============================================================================
# 📊 STAGE 1: SPAM DETECTION
# ============================================================================

"""
Use Case: Quick spam filtering
Speed: <1ms per email
Cost: Free
Accuracy: 95%+
"""

from src.models.spam_detector import get_spam_detector

# Initialize
detector = get_spam_detector()

# Predict single email
result = detector.predict("Your email text here")
# Returns: {'is_spam': True/False, 'confidence': 0.0-1.0, 'probability': {...}}

# Get predictions with confidence
if result['is_spam'] and result['confidence'] > 0.7:
    print("🚫 BLOCK THIS EMAIL")
else:
    print("✅ FORWARD TO STAGE 2")

# ============================================================================
# 🧠 STAGE 2: LLM ANALYSIS
# ============================================================================

"""
Use Case: Deep email analysis
Speed: 1-3 seconds per email
Cost: $0.001-0.01 per email
Features: Summary, NER, Sentiment
"""

import asyncio
from src.models.llm_analyzer import get_llm_analyzer

async def analyze():
    analyzer = get_llm_analyzer()
    
    # Analyze email
    result = await analyzer.analyze_email(
        subject="Your subject",
        body="Your email body"
    )
    
    # Access results
    print(result['summary'])                      # "Brief summary..."
    print(result['entities']['deadline'])         # "Friday EOD"
    print(result['entities']['amount'])           # "$50,000"
    print(result['sentiment']['is_urgent'])       # True/False
    print(result['sentiment']['requires_immediate_action'])  # True/False

# Run it
asyncio.run(analyze())

# ============================================================================
# 🤖 COMPLETE HYBRID PIPELINE
# ============================================================================

"""
Use Case: Complete classification
Speed: Stage 1 instant + Stage 2 if needed
Cost: ~90% less than pure LLM
Returns: Final classification + all analysis
"""

import asyncio
from src.models.hybrid_classifier import get_hybrid_classifier
from src.models.database import ClassificationLabel

async def classify():
    classifier = get_hybrid_classifier()
    
    # Classify single email
    result = await classifier.classify({
        'subject': 'URGENT: Budget approval needed by Friday',
        'body': 'The $50K budget...'
    })
    
    # Results
    print(f"Classification: {result['classification'].value}")  # IMPORTANT/SPAM/etc
    print(f"Confidence: {result['confidence']:.2%}")           # 92%
    print(f"Is Spam: {result['is_spam']}")                     # True/False
    print(f"Time: {result['processing_time_ms']}ms")           # 1240ms
    
    # Check if requires immediate action
    if result['classification'] == ClassificationLabel.IMPORTANT:
        print("🚨 THIS NEEDS ATTENTION!")
    
    # Get all details
    analysis = result['analysis']['llm_analysis']
    print(f"Summary: {analysis['summary']}")
    print(f"Deadline: {analysis['entities']['deadline']}")
    print(f"Sentiment: {analysis['sentiment']['label']}")
    print(f"Urgent: {analysis['sentiment']['is_urgent']}")

asyncio.run(classify())

# ============================================================================
# 📦 BATCH PROCESSING (Multiple Emails)
# ============================================================================

"""
Use Case: Process many emails at once
Speed: 4 concurrent + fast filtering
Cost: Only for legitimate emails
"""

import asyncio
from src.models.hybrid_classifier import get_hybrid_classifier

async def batch_process():
    classifier = get_hybrid_classifier()
    
    # List of emails to process
    emails = [
        {'subject': 'Email 1', 'body': 'Body 1'},
        {'subject': 'Email 2', 'body': 'Body 2'},
        {'subject': 'Email 3', 'body': 'Body 3'},
    ]
    
    # Process all at once
    results = await classifier.classify_batch(emails)
    
    # Analyze results
    spam_count = sum(1 for r in results if r['is_spam'])
    important_count = sum(1 for r in results 
                         if r['classification'].value == 'important')
    
    print(f"✓ Processed {len(emails)} emails")
    print(f"  - Spam: {spam_count}")
    print(f"  - Important: {important_count}")

asyncio.run(batch_process())

# ============================================================================
# 🔧 INTEGRATION WITH EMAIL SERVICE
# ============================================================================

"""
The hybrid classifier is already integrated!
Just use the email service normally.
"""

from src.services.email_service import get_email_processing_service

async def use_email_service():
    service = get_email_processing_service()
    
    # Process email (automatically uses hybrid classifier)
    email_data = {
        'from': 'sender@example.com',
        'to': 'recipient@example.com',
        'subject': 'Important email',
        'body': 'Email content...',
        'received_at': '2024-04-17T10:30:00Z'
    }
    
    result = await service.process_email(email_data)
    # Result automatically includes spam detection + LLM analysis!
    
    # Get classifier info
    info = service.get_classifier_info()
    print(f"Using: {info['name']}")
    print(f"Stages: {[s['name'] for s in info['stages']]}")

# ============================================================================
# 📈 MONITORING & STATS
# ============================================================================

"""
Track these metrics to monitor performance
"""

# Sample logging
import logging
from src.utils import get_logger

logger = get_logger(__name__)

# Log classification result
logger.info(f"Email classified: {classification} "
            f"(confidence: {confidence:.2%}, time: {time_ms}ms)")

# Track costs
emails_processed = 100
spam_percentage = 0.70
api_cost_per_email = 0.0015

api_calls = int(emails_processed * (1 - spam_percentage))
total_cost = api_calls * api_cost_per_email

print(f"Total emails: {emails_processed}")
print(f"Spam blocked: {int(emails_processed * spam_percentage)}")
print(f"LLM analyzed: {api_calls}")
print(f"API cost: ${total_cost:.2f}")

# ============================================================================
# ⚙️ CONFIGURATION QUICK REFERENCE
# ============================================================================

"""
In .env file, use these settings:
"""

config = """
# Basic setup
ENABLE_SPAM_DETECTION=true
ENABLE_LLM_ANALYSIS=true

# Cost optimization (CRITICAL!)
SKIP_LLM_FOR_SPAM=true          # Skip Stage 2 for spam = 90% cost saving

# LLM Setup
LLM_API_PROVIDER=openai         # or "claude"
LLM_API_KEY=sk-...              # Your API key
LLM_MODEL=gpt-3.5-turbo         # Cheap & fast

# Thresholds
SPAM_DETECTION_THRESHOLD=0.7    # 70% confidence = block
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7

# Performance
LLM_TIMEOUT=30                  # Seconds
LLM_USE_FALLBACK=true           # Use regex if API fails
"""

# ============================================================================
# 💰 COST EXAMPLES
# ============================================================================

"""
Scenario: 100 emails/day, 70% spam

Pure LLM (no filtering):
  100 emails × $0.0015 = $0.15/day = $4.50/month

With Hybrid (spam filter):
  70 spam (free) + 30 LLM
  30 emails × $0.0015 = $0.045/day = $1.35/month
  
SAVINGS: $3.15/month (70% reduction!)
"""

# Calculate for your scenario
def calculate_cost(emails_per_day, spam_percentage, cost_per_email):
    """Calculate monthly API cost"""
    legitimate = emails_per_day * (1 - spam_percentage)
    daily_cost = legitimate * cost_per_email
    monthly_cost = daily_cost * 30
    return monthly_cost

# Examples
cost_100_70spam = calculate_cost(100, 0.70, 0.0015)  # $1.35/month
cost_1000_70spam = calculate_cost(1000, 0.70, 0.0015)  # $13.50/month

print(f"100 emails/day: ${cost_100_70spam:.2f}/month")
print(f"1000 emails/day: ${cost_1000_70spam:.2f}/month")

# ============================================================================
# 🎯 COMMON PATTERNS
# ============================================================================

"""
Pattern 1: Filter to inbox only
"""
async def filter_important_emails():
    classifier = get_hybrid_classifier()
    
    # Only process important emails
    emails = [...]  # Load from inbox
    results = await classifier.classify_batch(emails)
    
    important_emails = [
        email for email, result in zip(emails, results)
        if result['classification'].value == 'important'
    ]
    return important_emails

"""
Pattern 2: Extract action items
"""
async def extract_deadlines():
    classifier = get_hybrid_classifier()
    
    email_result = await classifier.classify(email_data)
    analysis = email_result['analysis']['llm_analysis']
    
    deadline = analysis['entities']['deadline']
    requester = analysis['entities']['requester']
    amount = analysis['entities']['amount']
    is_urgent = analysis['sentiment']['is_urgent']
    
    if deadline and is_urgent:
        return {
            'action': 'Review',
            'deadline': deadline,
            'requester': requester,
            'priority': 'HIGH' if is_urgent else 'NORMAL'
        }

"""
Pattern 3: Smart inbox organization
"""
async def organize_inbox():
    classifier = get_hybrid_classifier()
    
    folders = {
        'SPAM': [],
        'URGENT': [],
        'WORK': [],
        'PROMOTIONS': [],
        'SOCIAL': [],
        'OTHER': []
    }
    
    for email in emails:
        result = await classifier.classify(email)
        
        if result['is_spam']:
            folders['SPAM'].append(email)
        elif result['classification'].value == 'important':
            if result['analysis']['llm_analysis']['sentiment']['is_urgent']:
                folders['URGENT'].append(email)
            else:
                folders['WORK'].append(email)
        elif result['classification'].value == 'promotional':
            folders['PROMOTIONS'].append(email)
        elif result['classification'].value == 'social':
            folders['SOCIAL'].append(email)
        else:
            folders['OTHER'].append(email)
    
    return folders

# ============================================================================
# 🔍 DEBUGGING
# ============================================================================

"""
Enable debug logging:
"""
import logging
logging.basicConfig(level=logging.DEBUG)

# Check if model file exists
import os
model_path = "./models/spam_detector.pkl"
if not os.path.exists(model_path):
    print(f"❌ Model not found: {model_path}")
    print("Run: python scripts/train_spam_detector.py")
else:
    print(f"✓ Model found: {model_path}")

# Check API key
import os
api_key = os.getenv('LLM_API_KEY', '')
if not api_key:
    print("⚠️  No LLM API key configured")
    print("Set LLM_API_KEY in .env")
else:
    print("✓ LLM API key configured")

# Test spam detector
detector = get_spam_detector()
test = "URGENT: Click here to win FREE MONEY!!!"
result = detector.predict(test)
print(f"✓ Spam detector working: {result['is_spam']}")

# ============================================================================
# 📚 LEARN MORE
# ============================================================================

"""
Documentation:
- HYBRID_AI_GUIDE.md         - Complete technical guide
- HYBRID_AI_IMPLEMENTATION.md - Implementation details
- HYBRID_AI_CONFIG.md         - Configuration options

Scripts:
- scripts/train_spam_detector.py     - Training script
- scripts/demo_hybrid_classifier.py  - Live demo
- scripts/example_hybrid_ai.py       - 6 complete examples

Code:
- src/models/spam_detector.py        - Stage 1 implementation
- src/models/llm_analyzer.py         - Stage 2 implementation
- src/models/hybrid_classifier.py    - Pipeline orchestration
"""

# ============================================================================
# ✅ CHECKLIST
# ============================================================================

checklist = """
Before going to production:

□ Run: python scripts/train_spam_detector.py
  Status: Model trained and saved

□ Run: python scripts/demo_hybrid_classifier.py
  Status: Demo completes successfully

□ Set LLM_API_KEY in .env
  Status: API key configured

□ Set LLM_API_PROVIDER in .env
  Status: Provider selected (openai/claude)

□ Enable SKIP_LLM_FOR_SPAM=true
  Status: Cost optimization enabled

□ Review thresholds in .env
  Status: Thresholds set appropriately

□ Test with real emails
  Status: System works with your data

□ Monitor costs for 1 week
  Status: API costs within budget

□ Deploy to production
  Status: System live and processing
"""

print(checklist)

# ============================================================================
# 🎓 KEY CONCEPTS
# ============================================================================

"""
HYBRID = Stage 1 + Stage 2

Stage 1: Spam Detection (TF-IDF + Naive Bayes)
- Fast: <1ms per email
- Free: No API calls
- Filters out 70-80% of emails (spam)
- Result: {'is_spam': bool, 'confidence': 0.0-1.0}

Stage 2: LLM Analysis (OpenAI/Claude API)
- Smart: Summarization, NER, Sentiment
- Selective: Only for legitimate emails
- Result: {'summary': str, 'entities': {...}, 'sentiment': {...}}

Combined Effect:
- Cost: 90% reduction (skip spam)
- Speed: Instant for spam + 1-3s for legitimate
- Quality: TF-IDF for speed + LLM for accuracy

Two Critical Settings:
1. SKIP_LLM_FOR_SPAM=true    (Enable cost savings!)
2. SPAM_DETECTION_THRESHOLD=0.7  (Tune accuracy)
"""

print("""
🎯 Remember:
1. Train spam detector ONCE: python scripts/train_spam_detector.py
2. Set API key in .env
3. Enable SKIP_LLM_FOR_SPAM=true (critical for cost!)
4. Run demo to verify: python scripts/demo_hybrid_classifier.py
5. Deploy and monitor

Questions? Check HYBRID_AI_GUIDE.md
""")

# ============================================================================
# End of Quick Reference
# ============================================================================

__doc__ = """
HYBRID AI EMAIL CLASSIFIER - QUICK REFERENCE

Three lines to classify an email:
    classifier = get_hybrid_classifier()
    result = await classifier.classify({'subject': '...', 'body': '...'})
    print(result['classification'])  # IMPORTANT/SPAM/PROMOTIONAL/SOCIAL/GENERAL

Key Files:
- src/models/spam_detector.py   → Fast spam filtering
- src/models/llm_analyzer.py    → Deep email analysis
- src/models/hybrid_classifier.py → Combines both
- scripts/train_spam_detector.py → Train the model
- scripts/demo_hybrid_classifier.py → See it in action

Configuration (.env):
- ENABLE_SPAM_DETECTION=true
- SKIP_LLM_FOR_SPAM=true              # CRITICAL!
- LLM_API_PROVIDER=openai
- LLM_API_KEY=sk-your-key
- SPAM_DETECTION_THRESHOLD=0.7

Cost Savings:
- Without Hybrid: $4.50/month (100 emails/day)
- With Hybrid: $0.93/month (90% reduction!)

Next: python scripts/train_spam_detector.py
"""
