#!/usr/bin/env python3
"""
Training script for Spam Detector

Trains TF-IDF + Naive Bayes model on spam vs normal emails
Usage: python scripts/train_spam_detector.py
"""

import sys
import pickle
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.spam_detector import SpamDetector, TRAINING_SPAM, TRAINING_NORMAL
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)

def load_training_data():
    """Load training data from file or use defaults"""
    # Default training data
    spam_texts = TRAINING_SPAM
    normal_texts = TRAINING_NORMAL
    
    logger.info(f"Loaded {len(spam_texts)} spam samples and {len(normal_texts)} normal samples")
    return spam_texts, normal_texts

def train_spam_detector():
    """Train and save spam detector model"""
    
    print("\n" + "="*60)
    print("🚀 Spam Detector Training")
    print("="*60)
    
    # Load training data
    spam_texts, normal_texts = load_training_data()
    
    # Initialize detector
    detector = SpamDetector()
    
    # Train
    print("\n📚 Training TF-IDF + Naive Bayes model...")
    accuracy = detector.train(spam_texts, normal_texts)
    
    print(f"\n✓ Model trained with {accuracy:.2%} accuracy")
    
    # Get feature importance
    features = detector.get_feature_names(top_n=15)
    
    print("\n📊 Top Important Features:")
    print("\nSpam Words:")
    for word in features.get('spam_words', [])[:10]:
        print(f"  • {word}")
    
    print("\nNormal Words:")
    for word in features.get('normal_words', [])[:10]:
        print(f"  • {word}")
    
    # Save model
    model_path = settings.spam_model_path
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    
    detector.save_model(model_path)
    print(f"\n💾 Model saved to: {model_path}")
    
    # Test predictions
    test_spam = "Congratulations! You've won $1000 click here now!!! viagra cialis"
    test_normal = "Meeting tomorrow at 2pm in conference room 4. Please confirm."
    
    print("\n🧪 Test Predictions:")
    
    spam_pred = detector.predict(test_spam)
    print(f"\nSpam email prediction:")
    print(f"  Is spam: {spam_pred['is_spam']}")
    print(f"  Confidence: {spam_pred['confidence']:.2%}")
    print(f"  Probabilities: spam={spam_pred['probability']['spam']:.2%}, normal={spam_pred['probability']['normal']:.2%}")
    
    normal_pred = detector.predict(test_normal)
    print(f"\nNormal email prediction:")
    print(f"  Is spam: {normal_pred['is_spam']}")
    print(f"  Confidence: {normal_pred['confidence']:.2%}")
    print(f"  Probabilities: spam={normal_pred['probability']['spam']:.2%}, normal={normal_pred['probability']['normal']:.2%}")
    
    print("\n" + "="*60)
    print("✅ Training complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        train_spam_detector()
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        sys.exit(1)
