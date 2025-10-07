import os
import shutil
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from typing import List, Dict, Any
import uuid
from datetime import datetime
import logging
import csv
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileHandler:
    """
    Medical-grade file handling for X-ray images
    """
    
    def __init__(self, upload_dir: str = "uploads", processed_dir: str = "processed"):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Allowed file extensions for medical images
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".dcm", ".dicom", ".tiff", ".tif"}
        self.max_file_size = 50 * 1024 * 1024  # 50MB max file size
        
        logger.info(f"📁 FileHandler initialized - Upload: {upload_dir}, Processed: {processed_dir}")
    
    def validate_image_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded image file
        """
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            logger.warning(f"❌ Invalid file extension: {file_ext}")
            return False
        
        # Check content type
        allowed_content_types = {
            "image/jpeg", "image/jpg", "image/png", 
            "image/tiff", "application/dicom",
            "application/octet-stream"  # For DICOM files
        }
        
        if file.content_type not in allowed_content_types:
            logger.warning(f"❌ Invalid content type: {file.content_type}")
            return False
        
        return True
    
    async def save_upload(self, file: UploadFile, upload_id: str) -> Path:
        """
        Save uploaded file to disk
        """
        try:
            # Generate safe filename
            original_name = file.filename
            file_ext = Path(original_name).suffix.lower()
            safe_filename = f"{upload_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
            
            file_path = self.upload_dir / safe_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as buffer:
                content = await file.read()
                
                # Check file size
                if len(content) > self.max_file_size:
                    raise ValueError(f"File size ({len(content)} bytes) exceeds maximum allowed ({self.max_file_size} bytes)")
                
                await buffer.write(content)
            
            logger.info(f"💾 Saved file: {safe_filename}")
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save file: {str(e)}")
            raise
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete file from disk
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"🗑️ Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete file: {str(e)}")
            return False
    
    def move_to_processed(self, file_path: Path, analysis_id: str) -> Path:
        """
        Move file to processed directory
        """
        try:
            processed_filename = f"processed_{analysis_id}_{file_path.name}"
            processed_path = self.processed_dir / processed_filename
            
            shutil.move(str(file_path), str(processed_path))
            logger.info(f"📂 Moved to processed: {processed_filename}")
            return processed_path
            
        except Exception as e:
            logger.error(f"❌ Failed to move file: {str(e)}")
            raise
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get file information
        """
        try:
            if not file_path.exists():
                return {}
            
            stat = file_path.stat()
            return {
                "filename": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix.lower()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get file info: {str(e)}")
            return {}
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up files older than specified days
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            # Clean upload directory
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            # Clean processed directory
            for file_path in self.processed_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            logger.info(f"🧹 Cleaned up {cleaned_count} old files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup files: {str(e)}")
            return 0
    
    def export_to_csv(self, analysis_results: List[Dict[str, Any]]) -> str:
        """
        Export analysis results to CSV format
        """
        try:
            output = io.StringIO()
            
            if not analysis_results:
                return ""
            
            # Define CSV headers
            headers = [
                "ID", "Filename", "Upload Time", "Analysis Time", 
                "Overall Status", "Confidence", "Processing Time (ms)",
                "L3 Status", "L4 Status", "L5 Status", "Sacrum Status",
                "L3-L4 Spacing (mm)", "L4-L5 Spacing (mm)", "L5-Sacrum Spacing (mm)",
                "Abnormalities Count", "Error Message"
            ]
            
            writer = csv.writer(output)
            writer.writerow(headers)
            
            for result in analysis_results:
                # Extract vertebrae analysis
                vertebrae_analysis = result.get('vertebrae_analysis', [])
                vertebrae_status = {}
                for vertebra in vertebrae_analysis:
                    vertebrae_status[vertebra.get('vertebra_type', '')] = vertebra.get('status', 'unknown')
                
                # Extract spacing measurements
                spacing_analysis = result.get('spacing_measurements', [])
                spacing_values = {}
                for spacing in spacing_analysis:
                    spacing_values[spacing.get('vertebra_pair', '')] = spacing.get('distance', 0.0)
                
                # Extract abnormalities
                abnormalities = result.get('abnormalities', [])
                abnormalities_count = len(abnormalities) if isinstance(abnormalities, list) else 0
                
                row = [
                    result.get('id', ''),
                    result.get('filename', ''),
                    result.get('uploaded_at', ''),
                    result.get('analyzed_at', ''),
                    result.get('overall_status', ''),
                    result.get('confidence', 0.0),
                    result.get('processing_time', 0.0),
                    vertebrae_status.get('L3', 'unknown'),
                    vertebrae_status.get('L4', 'unknown'),
                    vertebrae_status.get('L5', 'unknown'),
                    vertebrae_status.get('Sacrum', 'unknown'),
                    spacing_values.get('L3-L4', 0.0),
                    spacing_values.get('L4-L5', 0.0),
                    spacing_values.get('L5-Sacrum', 0.0),
                    abnormalities_count,
                    result.get('error_message', '')
                ]
                
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"📊 Exported {len(analysis_results)} results to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"❌ Failed to export CSV: {str(e)}")
            return ""
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """
        Get storage usage statistics
        """
        try:
            upload_size = sum(f.stat().st_size for f in self.upload_dir.rglob('*') if f.is_file())
            processed_size = sum(f.stat().st_size for f in self.processed_dir.rglob('*') if f.is_file())
            
            upload_count = len([f for f in self.upload_dir.iterdir() if f.is_file()])
            processed_count = len([f for f in self.processed_dir.iterdir() if f.is_file()])
            
            return {
                "upload_directory": {
                    "size_bytes": upload_size,
                    "size_mb": upload_size / (1024 * 1024),
                    "file_count": upload_count
                },
                "processed_directory": {
                    "size_bytes": processed_size,
                    "size_mb": processed_size / (1024 * 1024),
                    "file_count": processed_count
                },
                "total": {
                    "size_bytes": upload_size + processed_size,
                    "size_mb": (upload_size + processed_size) / (1024 * 1024),
                    "file_count": upload_count + processed_count
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to get storage usage: {str(e)}")
            return {}