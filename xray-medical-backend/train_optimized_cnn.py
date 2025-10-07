"""
Optimized CNN Training for X-ray Classification
Lightweight version with better resource management
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure TensorFlow
tf.config.optimizer.set_jit(True)  # Enable XLA JIT compilation
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF logging

class OptimizedXrayTrainer:
    """Optimized training pipeline for X-ray classification"""
    
    def __init__(self, dataset_path: str, img_size: tuple = (128, 128)):
        self.dataset_path = Path(dataset_path)
        self.img_size = img_size  # Smaller size for faster training
        
    def load_and_preprocess_data(self):
        """Load and preprocess all images efficiently"""
        logger.info("📂 Loading dataset...")
        
        images = []
        labels = []
        
        # Load normal images
        normal_path = self.dataset_path / 'normal'
        if normal_path.exists():
            for img_file in list(normal_path.glob('*.png'))[:100]:  # Limit for faster training
                img = self._load_image(str(img_file))
                if img is not None:
                    images.append(img)
                    labels.append(0)
        
        # Load abnormal images  
        abnormal_path = self.dataset_path / 'abnormal'
        if abnormal_path.exists():
            for img_file in list(abnormal_path.glob('*.png'))[:100]:  # Limit for faster training
                img = self._load_image(str(img_file))
                if img is not None:
                    images.append(img)
                    labels.append(1)
        
        logger.info(f"✅ Loaded {len(images)} images")
        logger.info(f"   Normal: {labels.count(0)}, Abnormal: {labels.count(1)}")
        
        return np.array(images), np.array(labels)
    
    def _load_image(self, path: str):
        """Load and preprocess single image"""
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # Grayscale for efficiency
            if img is None:
                return None
            
            # Resize and normalize
            img = cv2.resize(img, self.img_size)
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=-1)  # Add channel dimension
            
            return img
        except:
            return None
    
    def build_lightweight_model(self, input_shape):
        """Build lightweight CNN model"""
        logger.info("🔧 Building lightweight CNN model...")
        
        model = keras.Sequential([
            layers.Input(shape=input_shape),
            
            # First block
            layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Classification head
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
    
    def train_model(self, X, y, epochs=15):
        """Train the model efficiently"""
        logger.info("🚀 Starting efficient training...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        logger.info(f"Training: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
        
        # Build model
        model = self.build_lightweight_model(X_train.shape[1:])
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3
            )
        ]
        
        # Train with minimal augmentation
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rotation_range=5,
            width_shift_range=0.05,
            height_shift_range=0.05,
            horizontal_flip=True
        )
        
        # Train model
        history = model.fit(
            datagen.flow(X_train, y_train, batch_size=16),
            steps_per_epoch=len(X_train) // 16,
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        logger.info("📊 Evaluating model...")
        y_pred_prob = model.predict(X_test)
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        accuracy = np.mean(y_pred == y_test)
        report = classification_report(y_test, y_pred, 
                                     target_names=['Normal', 'Abnormal'],
                                     output_dict=True)
        
        logger.info(f"✅ Test Accuracy: {accuracy:.4f}")
        logger.info(f"   Normal - Precision: {report['Normal']['precision']:.4f}")
        logger.info(f"   Abnormal - Precision: {report['Abnormal']['precision']:.4f}")
        
        # Save model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"xray_classifier_{timestamp}.h5"
        model.save(model_path)
        logger.info(f"💾 Model saved: {model_path}")
        
        # Save report
        training_report = {
            'timestamp': timestamp,
            'accuracy': float(accuracy),
            'model_path': model_path,
            'dataset_size': len(X),
            'image_size': self.img_size,
            'epochs_trained': len(history.history['loss']),
            'classification_report': report
        }
        
        with open(f"training_report_{timestamp}.json", 'w') as f:
            json.dump(training_report, f, indent=2)
        
        return model, training_report

def main():
    """Main training function"""
    logger.info("🎯 Starting optimized X-ray classifier training...")
    
    # Initialize trainer
    trainer = OptimizedXrayTrainer("../datasets", img_size=(128, 128))
    
    # Load data
    X, y = trainer.load_and_preprocess_data()
    
    if len(X) == 0:
        logger.error("❌ No images loaded!")
        return
    
    # Train model
    model, report = trainer.train_model(X, y, epochs=15)
    
    logger.info("🎉 Training completed successfully!")
    logger.info(f"📈 Final accuracy: {report['accuracy']:.4f}")
    
    return model, report

if __name__ == "__main__":
    main()