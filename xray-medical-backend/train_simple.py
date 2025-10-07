#!/usr/bin/env python3
"""
Simple CNN Training for X-ray Classification
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_images(dataset_path, img_size=(128, 128), max_per_class=150):
    """Load images from dataset"""
    logger.info("Loading images...")
    
    images = []
    labels = []
    
    # Load normal images
    normal_path = Path(dataset_path) / 'normal'
    if normal_path.exists():
        count = 0
        for img_file in normal_path.glob('*.png'):
            if count >= max_per_class:
                break
            try:
                img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, img_size)
                    img = img.astype(np.float32) / 255.0
                    img = np.expand_dims(img, axis=-1)
                    images.append(img)
                    labels.append(0)
                    count += 1
            except:
                continue
    
    # Load abnormal images
    abnormal_path = Path(dataset_path) / 'abnormal'
    if abnormal_path.exists():
        count = 0
        for img_file in abnormal_path.glob('*.png'):
            if count >= max_per_class:
                break
            try:
                img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, img_size)
                    img = img.astype(np.float32) / 255.0
                    img = np.expand_dims(img, axis=-1)
                    images.append(img)
                    labels.append(1)
                    count += 1
            except:
                continue
    
    logger.info(f"Loaded {len(images)} images")
    logger.info(f"Normal: {labels.count(0)}, Abnormal: {labels.count(1)}")
    
    return np.array(images), np.array(labels)

def create_model(input_shape):
    """Create CNN model"""
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model():
    """Main training function"""
    # Load data
    X, y = load_images("../datasets", img_size=(128, 128), max_per_class=150)
    
    if len(X) == 0:
        print("No images loaded!")
        return
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    print(f"Training: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
    
    # Create model
    model = create_model(X_train.shape[1:])
    
    # Train
    history = model.fit(
        X_train, y_train,
        batch_size=32,
        epochs=20,
        validation_data=(X_val, y_val),
        verbose=1
    )
    
    # Evaluate
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    accuracy = np.mean(y_pred == y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"xray_classifier_{timestamp}.h5"
    model.save(model_path)
    print(f"Model saved: {model_path}")
    
    # Save report
    report = {
        'timestamp': timestamp,
        'accuracy': float(accuracy),
        'model_path': model_path,
        'dataset_size': len(X)
    }
    
    with open(f"training_report_{timestamp}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return model, report

if __name__ == "__main__":
    model, report = train_model()