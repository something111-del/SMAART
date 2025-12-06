"""
Spam Detection Model
ML classifier for detecting spam/fake content
"""

import pickle
import os
import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpamDetector:
    """
    Spam detection using TF-IDF + Logistic Regression
    """
    
    def __init__(self):
        """Initialize spam detector"""
        self.model = None
        self.vectorizer = None
        
        # Initialize MLflow
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment("smaart-spam-detection")
    
    def train(self, texts, labels):
        """
        Train spam detection model
        
        Args:
            texts: List of text samples
            labels: List of labels (0=ham, 1=spam)
        """
        logger.info("Training spam detector...")
        
        with mlflow.start_run():
            # Create pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', LogisticRegression(max_iter=1000, random_state=42))
            ])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )
            
            # Train
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            # Log metrics
            mlflow.log_param("max_features", 5000)
            mlflow.log_param("ngram_range", "(1, 2)")
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)
            
            # Log model
            mlflow.sklearn.log_model(self.model, "spam_detector")
            
            logger.info(f"Training complete - Accuracy: {accuracy:.4f}")
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
    
    def predict(self, text):
        """
        Predict if text is spam
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (is_spam, confidence)
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        prediction = self.model.predict([text])[0]
        probabilities = self.model.predict_proba([text])[0]
        confidence = max(probabilities)
        
        return bool(prediction), float(confidence)
    
    def save(self, path="./models/spam_detector.pkl"):
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"Model saved to {path}")
    
    def load(self, path="./models/spam_detector.pkl"):
        """Load model from disk"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {path}")
        else:
            logger.warning(f"Model file not found: {path}")
            # Train with dummy data for demo
            self._train_dummy_model()
    
    def _train_dummy_model(self):
        """Train with dummy data for demo purposes"""
        logger.info("Training with dummy data...")
        
        # Dummy training data
        texts = [
            "Buy now! Limited time offer!",
            "Click here to win $1000",
            "Meeting scheduled for tomorrow",
            "Please review the attached document",
            "FREE MONEY! Act now!",
            "Your package has been delivered",
            "Congratulations! You've won!",
            "The project deadline is next week",
        ]
        labels = [1, 1, 0, 0, 1, 0, 1, 0]  # 1=spam, 0=ham
        
        self.train(texts, labels)


if __name__ == "__main__":
    # Initialize and train
    detector = SpamDetector()
    detector._train_dummy_model()
    
    # Test
    test_texts = [
        "Free money! Click now!",
        "Meeting at 3pm tomorrow"
    ]
    
    for text in test_texts:
        is_spam, confidence = detector.predict(text)
        print(f"Text: {text}")
        print(f"Spam: {is_spam}, Confidence: {confidence:.2f}\n")
    
    # Save
    detector.save()
