"""
DistilBART Summarization Model
Wrapper for Hugging Face DistilBART model with MLflow tracking
"""

import os
import mlflow
import mlflow.transformers
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizationModel:
    """
    DistilBART-based summarization model with MLflow integration
    """
    
    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        """
        Initialize the summarization model
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize MLflow
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment("smaart-summarization")
        
        # Load model and tokenizer
        logger.info(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        
        # Create pipeline
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )
        
        logger.info("Model loaded successfully")
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
        do_sample: bool = False
    ) -> str:
        """
        Generate summary from text
        
        Args:
            text: Input text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            do_sample: Whether to use sampling
            
        Returns:
            Generated summary
        """
        try:
            # Log to MLflow
            with mlflow.start_run():
                mlflow.log_param("max_length", max_length)
                mlflow.log_param("min_length", min_length)
                mlflow.log_param("input_length", len(text))
                
                # Generate summary
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=do_sample,
                    truncation=True
                )
                
                summary = result[0]['summary_text']
                
                # Log metrics
                mlflow.log_metric("output_length", len(summary))
                mlflow.log_metric("compression_ratio", len(text) / len(summary))
                
                return summary
                
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            raise
    
    def batch_summarize(
        self,
        texts: List[str],
        max_length: int = 150,
        min_length: int = 50
    ) -> List[str]:
        """
        Summarize multiple texts in batch
        
        Args:
            texts: List of input texts
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            List of summaries
        """
        try:
            with mlflow.start_run():
                mlflow.log_param("batch_size", len(texts))
                mlflow.log_param("max_length", max_length)
                
                results = self.summarizer(
                    texts,
                    max_length=max_length,
                    min_length=min_length,
                    truncation=True,
                    batch_size=8
                )
                
                summaries = [r['summary_text'] for r in results]
                
                mlflow.log_metric("total_processed", len(summaries))
                
                return summaries
                
        except Exception as e:
            logger.error(f"Batch summarization error: {str(e)}")
            raise
    
    def save_model(self, path: str = "./models/distilbart"):
        """
        Save model to disk and log to MLflow
        
        Args:
            path: Directory to save model
        """
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save model and tokenizer
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            
            # Log to MLflow
            with mlflow.start_run():
                mlflow.transformers.log_model(
                    transformers_model={
                        "model": self.model,
                        "tokenizer": self.tokenizer
                    },
                    artifact_path="model",
                    registered_model_name="distilbart-summarizer"
                )
            
            logger.info(f"Model saved to {path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    @classmethod
    def load_model(cls, path: str):
        """
        Load model from disk
        
        Args:
            path: Directory containing saved model
            
        Returns:
            SummarizationModel instance
        """
        logger.info(f"Loading model from {path}")
        return cls(model_name=path)


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = SummarizationModel()
    
    # Test summarization
    test_text = """
    Artificial intelligence is rapidly transforming various industries. 
    Machine learning algorithms are being deployed in healthcare, finance, 
    and transportation. Recent breakthroughs in natural language processing 
    have enabled more sophisticated chatbots and translation systems. 
    However, concerns about AI ethics and job displacement remain significant 
    challenges that need to be addressed.
    """
    
    summary = model.summarize(test_text, max_length=100)
    print(f"Summary: {summary}")
    
    # Save model
    model.save_model()
