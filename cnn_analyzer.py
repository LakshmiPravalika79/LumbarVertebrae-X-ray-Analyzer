"""
CNN-based X-ray Analyzer for binary classification
Works in conjunction with Gemini AI for detailed analysis
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import cv2
from pathlib import Path
import logging
from typing import Tuple, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CNNXrayAnalyzer:
    """CNN-based analyzer for normal/abnormal classification"""
    
    def __init__(self, model_path: str = None, img_size: tuple = (224, 224)):
        self.model_path = model_path
        self.img_size = img_size
        self.model = None
        self.is_loaded = False
        
        # Try to load the model if path is provided
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained CNN model"""
        try:
            self.model = keras.models.load_model(model_path)
            self.model_path = model_path
            self.is_loaded = True
            logger.info(f"✅ CNN model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load CNN model: {e}")
            self.is_loaded = False
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for CNN prediction"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            img = cv2.resize(img, self.img_size)
            
            # Normalize pixel values
            img = img.astype(np.float32) / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            raise
    
    def predict_classification(self, image_path: str) -> Dict[str, Any]:
        """
        Predict normal/abnormal classification
        Returns confidence scores and classification
        """
        if not self.is_loaded:
            return {
                'available': False,
                'error': 'CNN model not loaded',
                'classification': 'unknown',
                'confidence': 0.0
            }
        
        try:
            # Preprocess image
            img = self.preprocess_image(image_path)
            
            # Make prediction
            prediction = self.model.predict(img, verbose=0)[0][0]
            
            # Convert to classification
            is_abnormal = prediction > 0.5
            confidence = float(prediction if is_abnormal else 1 - prediction)
            classification = 'abnormal' if is_abnormal else 'normal'
            
            result = {
                'available': True,
                'classification': classification,
                'confidence': confidence,
                'raw_score': float(prediction),
                'abnormal_probability': float(prediction),
                'normal_probability': float(1 - prediction),
                'model_path': self.model_path,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"CNN Classification: {classification} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"CNN prediction failed: {e}")
            return {
                'available': False,
                'error': str(e),
                'classification': 'unknown',
                'confidence': 0.0
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {'available': False, 'error': 'Model not loaded'}
        
        try:
            model_info = {
                'available': True,
                'model_path': self.model_path,
                'input_shape': self.model.input_shape,
                'output_shape': self.model.output_shape,
                'total_params': self.model.count_params(),
                'architecture': 'CNN for binary classification (normal/abnormal)'
            }
            return model_info
        except Exception as e:
            return {'available': False, 'error': str(e)}

def find_latest_model(models_dir: str = ".") -> str:
    """Find the most recently trained model"""
    models_dir = Path(models_dir)
    model_files = list(models_dir.glob("xray_classifier_*.h5"))
    
    if not model_files:
        return None
    
    # Sort by modification time, return most recent
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    return str(latest_model)

# Global CNN analyzer instance
cnn_analyzer = None

def initialize_cnn_analyzer(models_dir: str = ".") -> CNNXrayAnalyzer:
    """Initialize the global CNN analyzer"""
    global cnn_analyzer
    
    # Find latest model
    model_path = find_latest_model(models_dir)
    
    if model_path:
        logger.info(f"🤖 Initializing CNN analyzer with model: {model_path}")
        cnn_analyzer = CNNXrayAnalyzer(model_path)
    else:
        logger.warning("⚠️ No trained CNN model found. CNN analysis will be unavailable.")
        cnn_analyzer = CNNXrayAnalyzer()  # Initialize without model
    
    return cnn_analyzer

def get_cnn_analyzer() -> CNNXrayAnalyzer:
    """Get the global CNN analyzer instance"""
    global cnn_analyzer
    if cnn_analyzer is None:
        cnn_analyzer = initialize_cnn_analyzer()
    return cnn_analyzer