import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import logging
from typing import Tuple, Optional, Dict, Any
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Medical-grade image processing for X-ray analysis
    """
    
    def __init__(self):
        # Image processing parameters
        self.target_size = (1024, 1024)  # Standard size for analysis
        self.clahe_clip_limit = 3.0
        self.clahe_grid_size = (8, 8)
        self.gaussian_kernel_size = (5, 5)
        self.bilateral_filter_d = 9
        self.bilateral_filter_sigma_color = 75
        self.bilateral_filter_sigma_space = 75
        
        logger.info("🖼️ ImageProcessor initialized with medical parameters")
    
    async def preprocess_xray(self, image_path: Path) -> np.ndarray:
        """
        Preprocess X-ray image for analysis
        """
        try:
            # Load image
            image = self._load_image(image_path)
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Resize image to standard size
            image = self._resize_image(image, self.target_size)
            
            # Enhance contrast using CLAHE
            image = self._apply_clahe(image)
            
            # Reduce noise
            image = self._denoise_image(image)
            
            # Normalize intensity values
            image = self._normalize_intensity(image)
            
            # Enhance bone structures
            image = self._enhance_bone_structures(image)
            
            logger.info(f"✅ Preprocessed image: {image_path.name}")
            return image
            
        except Exception as e:
            logger.error(f"❌ Failed to preprocess image {image_path}: {str(e)}")
            raise
    
    def _load_image(self, image_path: Path) -> np.ndarray:
        """
        Load image from file with support for multiple formats
        """
        try:
            file_ext = image_path.suffix.lower()
            
            if file_ext in ['.dcm', '.dicom']:
                # Handle DICOM files (would require pydicom in production)
                logger.warning("DICOM support not fully implemented, loading as regular image")
                image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            else:
                # Load regular image formats
                image = cv2.imread(str(image_path))
            
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Failed to load image: {str(e)}")
            raise
    
    def _resize_image(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio
        """
        height, width = image.shape[:2]
        target_width, target_height = target_size
        
        # Calculate scaling factor
        scale = min(target_width / width, target_height / height)
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Create canvas and center the image
        canvas = np.zeros((target_height, target_width, resized.shape[2] if len(resized.shape) == 3 else 1), dtype=resized.dtype)
        if len(resized.shape) == 2:
            canvas = np.zeros((target_height, target_width), dtype=resized.dtype)
        
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        
        canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
        
        return canvas
    
    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Contrast Limited Adaptive Histogram Equalization
        """
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=self.clahe_grid_size
        )
        return clahe.apply(image)
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply denoising filters
        """
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(
            image,
            self.bilateral_filter_d,
            self.bilateral_filter_sigma_color,
            self.bilateral_filter_sigma_space
        )
        
        # Apply gentle Gaussian blur
        denoised = cv2.GaussianBlur(denoised, self.gaussian_kernel_size, 0)
        
        return denoised
    
    def _normalize_intensity(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image intensity values
        """
        # Convert to float
        normalized = image.astype(np.float32)
        
        # Normalize to 0-1 range
        normalized = (normalized - normalized.min()) / (normalized.max() - normalized.min())
        
        # Convert back to uint8
        normalized = (normalized * 255).astype(np.uint8)
        
        return normalized
    
    def _enhance_bone_structures(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance bone structures in X-ray image
        """
        # Apply morphological operations to enhance structures
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Morphological closing to fill small gaps
        enhanced = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Apply unsharp masking for edge enhancement
        gaussian = cv2.GaussianBlur(enhanced, (9, 9), 2.0)
        enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        # Clip values to valid range
        enhanced = np.clip(enhanced, 0, 255)
        
        return enhanced.astype(np.uint8)
    
    def extract_roi(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract region of interest from image
        """
        x, y, width, height = bbox
        
        # Ensure coordinates are within image bounds
        x = max(0, min(x, image.shape[1] - 1))
        y = max(0, min(y, image.shape[0] - 1))
        width = min(width, image.shape[1] - x)
        height = min(height, image.shape[0] - y)
        
        return image[y:y + height, x:x + width]
    
    def calculate_image_quality_metrics(self, image: np.ndarray) -> Dict[str, float]:
        """
        Calculate image quality metrics
        """
        try:
            # Convert to float for calculations
            img_float = image.astype(np.float32)
            
            # Calculate contrast (standard deviation)
            contrast = np.std(img_float)
            
            # Calculate brightness (mean intensity)
            brightness = np.mean(img_float)
            
            # Calculate sharpness using Laplacian variance
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # Calculate signal-to-noise ratio estimate
            # Use standard deviation as noise estimate
            signal = np.mean(img_float)
            noise = np.std(img_float)
            snr = signal / noise if noise > 0 else 0
            
            # Calculate dynamic range
            dynamic_range = np.max(img_float) - np.min(img_float)
            
            return {
                "contrast": float(contrast),
                "brightness": float(brightness),
                "sharpness": float(sharpness),
                "snr": float(snr),
                "dynamic_range": float(dynamic_range)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate quality metrics: {str(e)}")
            return {}
    
    def create_thumbnail(self, image: np.ndarray, size: Tuple[int, int] = (200, 200)) -> np.ndarray:
        """
        Create thumbnail image
        """
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    
    def save_processed_image(self, image: np.ndarray, output_path: Path) -> bool:
        """
        Save processed image to disk
        """
        try:
            success = cv2.imwrite(str(output_path), image)
            if success:
                logger.info(f"💾 Saved processed image: {output_path}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to save image: {str(e)}")
            return False
    
    async def batch_preprocess(self, image_paths: list[Path]) -> list[np.ndarray]:
        """
        Preprocess multiple images concurrently
        """
        tasks = [self.preprocess_xray(path) for path in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        processed_images = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Failed to process {image_paths[i]}: {str(result)}")
            else:
                processed_images.append(result)
        
        return processed_images