"""
File Handling Utilities
Secure file operations and management
"""

import os
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Secure file handling for uploaded documents.
    
    Features:
    - Secure file storage with sanitized names
    - Temporary file management
    - File cleanup and rotation
    - Upload size and type validation
    """
    
    def __init__(self, upload_folder: str = "uploads", temp_folder: str = "temp"):
        self.upload_folder = Path(upload_folder)
        self.temp_folder = Path(temp_folder)
        
      
        self.upload_folder.mkdir(exist_ok=True)
        self.temp_folder.mkdir(exist_ok=True)
        
        logger.info(f"FileHandler initialized - Upload: {self.upload_folder}, Temp: {self.temp_folder}")
    
    def save_uploaded_file(self, file: FileStorage, custom_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Securely save uploaded file.
        
        Args:
            file: Uploaded file object
            custom_name: Optional custom filename
            
        Returns:
            Dictionary with file information
        """
        try:
            if not file or not file.filename:
                raise ValueError("No file provided")
            
          
            original_filename = file.filename
            if custom_name:
                filename = secure_filename(custom_name)
            else:
                filename = secure_filename(original_filename)
            
          
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            # Save file
            file_path = self.upload_folder / unique_filename
            file.save(str(file_path))
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            
            # Get file stats
            file_stats = file_path.stat()
            
            file_info = {
                'original_name': original_filename,
                'saved_name': unique_filename,
                'file_path': str(file_path),
                'file_size': file_stats.st_size,
                'upload_time': datetime.now().isoformat(),
                'file_hash': file_hash,
                'extension': ext.lower()
            }
            
            logger.info(f"File saved successfully: {unique_filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise
    
    def create_temp_file(self, suffix: str = "", prefix: str = "ocr_") -> str:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix (e.g., '.pdf', '.png')
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=suffix, 
                prefix=prefix, 
                dir=str(self.temp_folder)
            )
            
          
            os.close(temp_fd)
            
            logger.debug(f"Temporary file created: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temporary file: {e}")
            raise
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files.
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
            
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_folder.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"Cleaned up old temp file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to delete temp file {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} temporary files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
            return 0
    
    def cleanup_upload_files(self, max_age_days: int = 7) -> int:
        """
        Clean up old uploaded files.
        
        Args:
            max_age_days: Maximum age of files to keep (in days)
            
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 3600
            
            for file_path in self.upload_folder.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"Cleaned up old upload file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to delete upload file {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} uploaded files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Upload file cleanup failed: {e}")
            return 0
    
    def delete_file(self, file_path: str) -> bool:
        """
        Safely delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            
            if path.exists() and path.is_file():
                path.unlink()
                logger.debug(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            stats = path.stat()
            
            return {
                'name': path.name,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'extension': path.suffix.lower(),
                'is_file': path.is_file(),
                'absolute_path': str(path.absolute())
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy a file to a new location.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if not source.exists():
                logger.error(f"Source file not found: {source_path}")
                return False
            
          
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, destination)
            
            logger.debug(f"File copied: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file {source_path} -> {destination_path}: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move a file to a new location.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if not source.exists():
                logger.error(f"Source file not found: {source_path}")
                return False
            
         
            destination.parent.mkdir(parents=True, exist_ok=True)
            
         
            shutil.move(str(source), str(destination))
            
            logger.debug(f"File moved: {source_path} -> {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file {source_path} -> {destination_path}: {e}")
            return False
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get disk usage information for upload and temp directories.
        
        Returns:
            Disk usage information
        """
        try:
            usage_info = {}
            
         
            upload_size = self._calculate_directory_size(self.upload_folder)
            usage_info['upload_folder'] = {
                'path': str(self.upload_folder),
                'size_bytes': upload_size,
                'size_mb': round(upload_size / (1024 * 1024), 2)
            }
            
          
            temp_size = self._calculate_directory_size(self.temp_folder)
            usage_info['temp_folder'] = {
                'path': str(self.temp_folder),
                'size_bytes': temp_size,
                'size_mb': round(temp_size / (1024 * 1024), 2)
            }
            
           
            disk_usage = shutil.disk_usage(str(self.upload_folder))
            usage_info['disk'] = {
                'total_bytes': disk_usage.total,
                'used_bytes': disk_usage.used,
                'free_bytes': disk_usage.free,
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 2)
            }
            
            return usage_info
            
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return {}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.warning(f"Failed to calculate file hash: {e}")
            return ""
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of all files in a directory."""
        try:
            total_size = 0
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            logger.warning(f"Failed to calculate directory size: {e}")
            return 0
    
    def list_files(self, directory: Optional[str] = None, 
                   pattern: str = "*", limit: int = 100) -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            directory: Directory to list (defaults to upload folder)
            pattern: File pattern to match
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            if directory:
                search_dir = Path(directory)
            else:
                search_dir = self.upload_folder
            
            if not search_dir.exists():
                return []
            
            files = []
            
            for file_path in search_dir.glob(pattern):
                if file_path.is_file() and len(files) < limit:
                    file_info = self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory_path}: {e}")
            return False