# Hybrid AI Configuration Reference

## Environment Variables (.env)

Copy and customize these values in your `.env` file:

```env
# ============================================================================
# STAGE 1: SPAM DETECTION (TF-IDF + Naive Bayes)
# ============================================================================

# Enable spam detection pipeline
ENABLE_SPAM_DETECTION=true

# Path to trained spam detector model
# This file is created by: python scripts/train_spam_detector.py
SPAM_MODEL_PATH=./models/spam_detector.pkl

# Spam confidence threshold (0.0 - 1.0)
# Emails with spam confidence > this value are blocked
# Recommended: 0.7 (70%)
# Higher = fewer false positives, more spam gets through
# Lower = better spam catching, more false positives
SPAM_DETECTION_THRESHOLD=0.7

# ============================================================================
# STAGE 2: LLM ANALYSIS (Summarization + NER + Sentiment)
# ============================================================================

# Enable LLM analysis for non-spam emails
ENABLE_LLM_ANALYSIS=true

# LLM API Provider
# Options: "openai" or "claude"
LLM_API_PROVIDER=openai

# LLM API Key
# Get from: https://platform.openai.com/account/api-keys
# Or: https://console.anthropic.com
# IMPORTANT: Keep this secret! Use environment variables, not in code
LLM_API_KEY=sk-your-api-key-here

# LLM Model Selection
# OpenAI models: gpt-3.5-turbo (cheap), gpt-4 (expensive but better)
# Claude models: claude-3-sonnet (balanced), claude-3-opus (best)
LLM_MODEL=gpt-3.5-turbo

# LLM API timeout (seconds)
# How long to wait for LLM response before timeout
LLM_TIMEOUT=30

# LLM API retry count
# How many times to retry if API call fails
LLM_MAX_RETRIES=2

# Fallback to heuristics if LLM API is unavailable
# When enabled: uses regex + keyword matching if API fails
# When disabled: returns error if API fails
LLM_USE_FALLBACK=true

# ============================================================================
# HYBRID PIPELINE BEHAVIOR
# ============================================================================

# Skip expensive LLM processing for spam emails
# CRITICAL: Enable this to save 40-60% on API costs!
# When enabled: Spam emails skip Stage 2 entirely (free!)
# When disabled: Even spam gets analyzed by LLM (expensive!)
SKIP_LLM_FOR_SPAM=true

# Classification confidence threshold (0.0 - 1.0)
# Classification is only returned if confidence >= this threshold
# Otherwise, email gets default classification (GENERAL)
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7

# ============================================================================
# ADVANCED: Model Fine-tuning
# ============================================================================

# Batch processing concurrency
# How many emails to analyze in parallel
# Higher = faster but uses more memory
# Recommended: 4 for most setups
HYBRID_BATCH_SIZE=4

# Process timeout per email (milliseconds)
# Maximum time allowed for complete hybrid classification
HYBRID_PROCESS_TIMEOUT_MS=5000

# ============================================================================
# EXAMPLES: DIFFERENT CONFIGURATIONS
# ============================================================================

# --- BUDGET MODE: Minimize API costs ---
# Recommended for: Large volume, cost-sensitive
ENABLE_SPAM_DETECTION=true
SPAM_DETECTION_THRESHOLD=0.8        # Very strict
ENABLE_LLM_ANALYSIS=true
SKIP_LLM_FOR_SPAM=true              # CRITICAL!
LLM_API_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo             # Cheapest
LLM_TIMEOUT=20                      # Timeout faster

# --- ACCURACY MODE: Best quality analysis ---
# Recommended for: Mission-critical, high accuracy needed
ENABLE_SPAM_DETECTION=true
SPAM_DETECTION_THRESHOLD=0.5        # Less strict
ENABLE_LLM_ANALYSIS=true
SKIP_LLM_FOR_SPAM=false             # Analyze everything
LLM_API_PROVIDER=openai
LLM_MODEL=gpt-4                     # Best quality
LLM_TIMEOUT=60                      # More time

# --- FAST MODE: Speed prioritized ---
# Recommended for: Real-time processing, low latency
ENABLE_SPAM_DETECTION=true
SPAM_DETECTION_THRESHOLD=0.7
ENABLE_LLM_ANALYSIS=true
SKIP_LLM_FOR_SPAM=true
LLM_API_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_USE_FALLBACK=true               # Fallback is faster
HYBRID_BATCH_SIZE=8                 # More parallel
HYBRID_PROCESS_TIMEOUT_MS=3000      # Quick timeout

# --- DEVELOPMENT MODE: No API keys needed ---
# Recommended for: Local testing, development
ENABLE_SPAM_DETECTION=true
SPAM_MODEL_PATH=./models/spam_detector.pkl
ENABLE_LLM_ANALYSIS=true
LLM_API_KEY=                        # Empty!
LLM_USE_FALLBACK=true               # Uses heuristics only
# System works completely without LLM API

# ============================================================================
# API KEY SETUP INSTRUCTIONS
# ============================================================================

# OpenAI Setup:
# 1. Go to: https://platform.openai.com/account/api-keys
# 2. Create new API key
# 3. Copy key (starts with "sk-")
# 4. Paste into LLM_API_KEY
# 5. Save .env file

# Example:
# LLM_API_PROVIDER=openai
# LLM_API_KEY=sk-proj-abc123def456...xyz

# Claude Setup:
# 1. Go to: https://console.anthropic.com/account/keys
# 2. Create new API key
# 3. Copy key (starts with "sk-ant-")
# 4. Paste into LLM_API_KEY
# 5. Save .env file

# Example:
# LLM_API_PROVIDER=claude
# LLM_API_KEY=sk-ant-abc123def456...xyz

# ============================================================================
# COST CALCULATOR
# ============================================================================

# Prices (as of 2024):
# gpt-3.5-turbo: $0.0015 per 1K tokens (~1-2 emails)
# gpt-4: $0.03 per 1K tokens (~1-2 emails)
# claude-3-sonnet: $0.003 per 1K tokens
# claude-3-opus: $0.015 per 1K tokens

# Scenario: 100 emails/day, 70% spam

# Pure LLM (no spam filter):
# 100 emails × $0.0015 = $0.15/day = $4.50/month

# With Hybrid (spam filter enabled):
# 70 spam blocked (free)
# 30 legitimate × $0.0015 = $0.045/day = $1.35/month
# SAVINGS: $3.15/month (70% reduction!)

# ============================================================================
# FEATURE REFERENCE
# ============================================================================

# Stage 1: Spam Detection
# ├─ TF-IDF Vectorization
# │  └─ Converts text to numbers
# ├─ Naive Bayes Classification
# │  └─ Fast probability calculation
# ├─ Pre-trained Model
# │  └─ 20+ training samples (95%+ accuracy)
# └─ Custom Training
#    └─ Can train on your own data

# Stage 2: LLM Analysis
# ├─ Summarization
# │  └─ 2-3 sentence summary
# ├─ NER (Named Entity Recognition)
# │  ├─ Extract deadline
# │  ├─ Extract requester
# │  ├─ Extract amount
# │  └─ Extract other entities
# ├─ Sentiment Analysis
# │  ├─ Emotion (positive/negative/neutral)
# │  ├─ Urgency detection
# │  └─ Action required flag
# └─ Classification
#    ├─ IMPORTANT (urgent + deadline)
#    ├─ PROMOTIONAL (amount + positive)
#    ├─ SOCIAL (personal)
#    └─ GENERAL (default)

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# For maximum speed:
SPAM_DETECTION_THRESHOLD=0.9        # Stricter filter
SKIP_LLM_FOR_SPAM=true
LLM_USE_FALLBACK=true               # Fallback is faster
LLM_TIMEOUT=15
HYBRID_BATCH_SIZE=8

# For maximum accuracy:
SPAM_DETECTION_THRESHOLD=0.5        # Looser filter
SKIP_LLM_FOR_SPAM=false             # Analyze everything
LLM_MODEL=gpt-4                     # Better model
LLM_TIMEOUT=60
HYBRID_BATCH_SIZE=2                 # More careful processing

# For minimum cost:
ENABLE_SPAM_DETECTION=true
SKIP_LLM_FOR_SPAM=true              # CRITICAL!
LLM_MODEL=gpt-3.5-turbo             # Cheapest
HYBRID_BATCH_SIZE=16                # Batch more

# ============================================================================
# MONITORING & LOGGING
# ============================================================================

# These are automatically logged for each email:
# - is_spam: boolean
# - spam_confidence: 0.0 - 1.0
# - processing_time_ms: milliseconds
# - classification: SPAM/IMPORTANT/PROMOTIONAL/SOCIAL/GENERAL
# - sentiment: label, score, urgency
# - entities: deadline, requester, amount
# - llm_api_calls: count of API calls used
# - api_cost: estimated cost of this email

# Monitor with:
# 1. Check logs: docker logs ai-email-classifier
# 2. Query MongoDB: db.processed_emails.find()
# 3. API endpoint: GET /api/v1/stats

# ============================================================================
# COMMON ISSUES & SOLUTIONS
# ============================================================================

# Issue: "Model file not found"
# Solution: Run: python scripts/train_spam_detector.py

# Issue: "LLM API timeout"
# Solution: Increase LLM_TIMEOUT to 60

# Issue: "High API costs"
# Solution: Set SKIP_LLM_FOR_SPAM=true (most important!)

# Issue: "Low spam detection accuracy"
# Solution: Adjust SPAM_DETECTION_THRESHOLD down (0.5-0.6)

# Issue: "API key invalid"
# Solution: Check API key format and re-copy from provider

# Issue: "Slow processing"
# Solution: Increase HYBRID_BATCH_SIZE or use gpt-3.5-turbo

# ============================================================================

# Generated: 2024-04-17
# Last Updated: 2024-04-17
