"""
CNN Training Pipeline for X-ray Classification
Trains a deep learning model to classify normal vs abnormal X-rays
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XrayDataProcessor:
    """Handles data loading and preprocessing for X-ray images"""
    
    def __init__(self, dataset_path: str, img_size: tuple = (224, 224)):
        self.dataset_path = Path(dataset_path)
        self.img_size = img_size
        self.images = []
        self.labels = []
        self.class_names = ['normal', 'abnormal']
        
    def load_images(self):
        """Load and preprocess images from normal and abnormal folders"""
        logger.info("Loading dataset images...")
        
        # Load normal images (label = 0)
        normal_path = self.dataset_path / 'normal'
        if normal_path.exists():
            for img_file in normal_path.glob('*.png'):
                img = self._preprocess_image(str(img_file))
                if img is not None:
                    self.images.append(img)
                    self.labels.append(0)  # 0 = normal
                    
        # Load abnormal images (label = 1)
        abnormal_path = self.dataset_path / 'abnormal'
        if abnormal_path.exists():
            for img_file in abnormal_path.glob('*.png'):
                img = self._preprocess_image(str(img_file))
                if img is not None:
                    self.images.append(img)
                    self.labels.append(1)  # 1 = abnormal
                    
        logger.info(f"Loaded {len(self.images)} images total")
        logger.info(f"Normal: {self.labels.count(0)}, Abnormal: {self.labels.count(1)}")
        
        return np.array(self.images), np.array(self.labels)
    
    def _preprocess_image(self, img_path: str):
        """Preprocess individual image"""
        try:
            # Read image
            img = cv2.imread(img_path)
            if img is None:
                logger.warning(f"Could not load image: {img_path}")
                return None
                
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to target size
            img = cv2.resize(img, self.img_size)
            
            # Normalize pixel values to [0, 1]
            img = img.astype(np.float32) / 255.0
            
            return img
            
        except Exception as e:
            logger.error(f"Error processing image {img_path}: {e}")
            return None

class XrayClassificationModel:
    """CNN model for X-ray classification"""
    
    def __init__(self, input_shape: tuple = (224, 224, 3)):
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build CNN architecture optimized for medical imaging"""
        logger.info("Building CNN model...")
        
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third convolutional block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Fourth convolutional block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Global average pooling instead of flatten to reduce overfitting
            layers.GlobalAveragePooling2D(),
            
            # Dense layers
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            # Output layer for binary classification
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        logger.info("Model built successfully!")
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50):
        """Train the model"""
        logger.info(f"Starting training for {epochs} epochs...")
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=0.0001
            ),
            keras.callbacks.ModelCheckpoint(
                'best_xray_model.h5',
                monitor='val_accuracy',
                save_best_only=True,
                mode='max'
            )
        ]
        
        # Data augmentation
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            zoom_range=0.1,
            fill_mode='nearest'
        )
        
        # Train model
        self.history = self.model.fit(
            datagen.flow(X_train, y_train, batch_size=32),
            steps_per_epoch=len(X_train) // 32,
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Training completed!")
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        logger.info("Evaluating model...")
        
        # Predictions
        y_pred_prob = self.model.predict(X_test)
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        # Classification report
        report = classification_report(y_test, y_pred, 
                                     target_names=['Normal', 'Abnormal'],
                                     output_dict=True)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        logger.info(f"Accuracy: {report['accuracy']:.4f}")
        logger.info(f"Normal - Precision: {report['Normal']['precision']:.4f}, Recall: {report['Normal']['recall']:.4f}")
        logger.info(f"Abnormal - Precision: {report['Abnormal']['precision']:.4f}, Recall: {report['Abnormal']['recall']:.4f}")
        
        return report, cm, y_pred_prob
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")

def train_xray_classifier(dataset_path: str):
    """Main training pipeline"""
    logger.info("🚀 Starting X-ray classification training pipeline...")
    
    # Initialize data processor
    processor = XrayDataProcessor(dataset_path)
    
    # Load and preprocess data
    X, y = processor.load_images()
    
    if len(X) == 0:
        raise ValueError("No images loaded. Check dataset path and image files.")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    logger.info(f"Training set: {len(X_train)} images")
    logger.info(f"Validation set: {len(X_val)} images")
    logger.info(f"Test set: {len(X_test)} images")
    
    # Build and train model
    model = XrayClassificationModel()
    model.build_model()
    
    # Print model summary
    model.model.summary()
    
    # Train model
    history = model.train(X_train, y_train, X_val, y_val, epochs=30)
    
    # Evaluate model
    report, cm, predictions = model.evaluate(X_test, y_test)
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"xray_classifier_{timestamp}.h5"
    model.save_model(model_path)
    
    # Save training report
    training_report = {
        'timestamp': timestamp,
        'dataset_info': {
            'total_images': len(X),
            'normal_count': int((y == 0).sum()),
            'abnormal_count': int((y == 1).sum()),
            'train_size': len(X_train),
            'val_size': len(X_val),
            'test_size': len(X_test)
        },
        'performance': report,
        'confusion_matrix': cm.tolist(),
        'model_path': model_path
    }
    
    with open(f"training_report_{timestamp}.json", 'w') as f:
        json.dump(training_report, f, indent=2)
    
    logger.info("🎉 Training pipeline completed successfully!")
    logger.info(f"Model saved as: {model_path}")
    
    return model, training_report

if __name__ == "__main__":
    # Run training
    dataset_path = "../datasets"  # Go up one level to find datasets folder
    model, report = train_xray_classifier(dataset_path)