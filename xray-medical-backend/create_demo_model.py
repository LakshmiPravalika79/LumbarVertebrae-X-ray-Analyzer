"""
Mock CNN Model for Demonstration
Creates a simple pre-trained model for testing the hybrid analyzer
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
from datetime import datetime
import json

def create_demo_model():
    """Create a simple CNN model for demonstration"""
    model = keras.Sequential([
        layers.Input(shape=(128, 128, 1)),
        
        layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),
        
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),
        
        layers.GlobalAveragePooling2D(),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def create_mock_trained_model():
    """Create and save a mock trained model"""
    print("Creating mock trained CNN model for demonstration...")
    
    # Create model
    model = create_demo_model()
    
    # Create dummy training data for weight initialization
    dummy_X = np.random.random((10, 128, 128, 1))
    dummy_y = np.random.randint(0, 2, (10,))
    
    # Train for just 1 epoch to initialize weights properly
    model.fit(dummy_X, dummy_y, epochs=1, verbose=0)
    
    # Save model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"xray_classifier_{timestamp}.h5"
    model.save(model_path)
    
    # Create training report
    report = {
        'timestamp': timestamp,
        'model_path': model_path,
        'model_type': 'demo_cnn',
        'accuracy': 0.85,  # Mock accuracy
        'dataset_size': 160,  # Mock dataset size
        'image_size': [128, 128],
        'epochs_trained': 15,
        'note': 'Demo model for hybrid analyzer testing'
    }
    
    with open(f"training_report_{timestamp}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Mock model saved: {model_path}")
    print(f"Mock accuracy: {report['accuracy']:.1%}")
    
    return model, report

if __name__ == "__main__":
    model, report = create_mock_trained_model()