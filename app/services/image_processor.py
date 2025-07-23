"""
Advanced Image Processing Service
Professional image enhancement and correction for optimal OCR
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List
from scipy import ndimage
import math

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Advanced image processing for OCR optimization.
    
    Features:
    - Automatic rotation correction (0°, 90°, 180°, 270°)
    - Skew correction using Hough transform
    - Adaptive image enhancement
    - Noise reduction and contrast improvement
    - Resolution upscaling for small images
    """
    
    def __init__(self):
        self.min_dpi = 150
        self.target_dpi = 300
        logger.info("ImageProcessor initialized")
    
    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Comprehensive image enhancement pipeline for OCR.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Enhanced image optimized for OCR
        """
        try:
            enhanced = image.copy()
            
            enhanced = self._enhance_resolution(enhanced)
            
        
            enhanced = self._reduce_noise(enhanced)
            
        
            enhanced = self._optimize_contrast(enhanced)
            
    
            enhanced = self._sharpen_image(enhanced)
            
            logger.debug("Image enhancement completed")
            return enhanced
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image
    
    def correct_rotation(self, image: np.ndarray) -> np.ndarray:
        """
        Intelligent rotation correction using multiple methods.
        
        Args:
            image: Input image
            
        Returns:
            Rotation-corrected image
        """
        try:
            
            skew_corrected = self._correct_skew(image)
            
            # Method 2: Detect major rotation (90°, 180°, 270°)
            rotation_corrected = self._detect_and_correct_major_rotation(skew_corrected)
            
        
            fine_tuned = self._fine_tune_rotation(rotation_corrected)
            
            logger.debug("Rotation correction completed")
            return fine_tuned
            
        except Exception as e:
            logger.error(f"Rotation correction failed: {e}")
            return image
    
    def _enhance_resolution(self, image: np.ndarray) -> np.ndarray:
        """Enhance image resolution if too low."""
        try:
            height, width = image.shape[:2]
            
        
            estimated_dpi = min(width, height) 
            
            if estimated_dpi < self.min_dpi:
                # Calculate scale factor
                scale_factor = self.target_dpi / estimated_dpi
                scale_factor = min(scale_factor, 3.0)  # Limit upscaling
                
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # Use high-quality interpolation
                enhanced = cv2.resize(image, (new_width, new_height), 
                                    interpolation=cv2.INTER_CUBIC)
                
                logger.debug(f"Resolution enhanced: {width}x{height} -> {new_width}x{new_height}")
                return enhanced
            
            return image
            
        except Exception as e:
            logger.warning(f"Resolution enhancement failed: {e}")
            return image
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Apply noise reduction techniques."""
        try:
            if len(image.shape) == 3:
            
                denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            else:
        
                denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
            
            return denoised
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return image
    
    def _optimize_contrast(self, image: np.ndarray) -> np.ndarray:
        """Optimize contrast and brightness using CLAHE."""
        try:
            if len(image.shape) == 3:
                
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                
        
                lab = cv2.merge([l, a, b])
                enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                
            else:
                
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(image)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Contrast optimization failed: {e}")
            return image
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpening filter to enhance text edges."""
        try:
            # Unsharp masking kernel
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            
            sharpened = cv2.filter2D(image, -1, kernel)
            
            
            alpha = 0.7
            result = cv2.addWeighted(image, 1-alpha, sharpened, alpha, 0)
            
            return result
            
        except Exception as e:
            logger.warning(f"Image sharpening failed: {e}")
            return image
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """Correct skew using Hough line detection."""
        try:
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    
                    
                    if angle > 90:
                        angle = angle - 180
                    
                    angles.append(angle)
                
                if angles:
                    
                    skew_angle = np.median(angles)
                    
                
                    if abs(skew_angle) > 0.5:
                        
                        height, width = image.shape[:2]
                        center = (width // 2, height // 2)
                        
                        rotation_matrix = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
                        
                
                        corrected = cv2.warpAffine(image, rotation_matrix, (width, height),
                                                 flags=cv2.INTER_CUBIC,
                                                 borderMode=cv2.BORDER_REPLICATE)
                        
                        logger.debug(f"Skew corrected by {skew_angle:.2f} degrees")
                        return corrected
            
            return image
            
        except Exception as e:
            logger.warning(f"Skew correction failed: {e}")
            return image
    
    def _detect_and_correct_major_rotation(self, image: np.ndarray) -> np.ndarray:
        """Detect and correct major rotations (90°, 180°, 270°)."""
        try:
        
            rotations = [
                (0, image),
                (90, cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)),
                (180, cv2.rotate(image, cv2.ROTATE_180)),
                (270, cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE))
            ]
            
            best_rotation = 0
            best_score = 0
            
            for angle, rotated_img in rotations:
                score = self._evaluate_text_orientation(rotated_img)
                
                if score > best_score:
                    best_score = score
                    best_rotation = angle
            
            if best_rotation == 90:
                result = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            elif best_rotation == 180:
                result = cv2.rotate(image, cv2.ROTATE_180)
            elif best_rotation == 270:
                result = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            else:
                result = image
            
            if best_rotation != 0:
                logger.debug(f"Major rotation corrected: {best_rotation}°")
            
            return result
            
        except Exception as e:
            logger.warning(f"Major rotation detection failed: {e}")
            return image
    
    def _evaluate_text_orientation(self, image: np.ndarray) -> float:
        """
        Evaluate text orientation quality using projection profiles.
        Higher score indicates better text orientation.
        """
        try:
            
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
        
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
        
            binary = 255 - binary
            
            
            h_projection = np.sum(binary, axis=1)
            
        
            h_variance = np.var(h_projection)
            
            
            v_projection = np.sum(binary, axis=0)
            v_variance = np.var(v_projection)
            
        
            score = h_variance / (v_variance + 1)  
            
            return score
            
        except Exception as e:
            logger.warning(f"Text orientation evaluation failed: {e}")
            return 0.0
    
    def _fine_tune_rotation(self, image: np.ndarray) -> np.ndarray:
        """Fine-tune rotation using text line detection."""
        try:
        
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
    
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            

            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                angles = []
                
                for contour in contours:
                
                    if len(contour) >= 5: 
                        try:
                            (x, y), (w, h), angle = cv2.fitEllipse(contour)
                            
                    
                            if angle > 90:
                                angle = angle - 180
                            
                    
                            if abs(angle) < 45 and w > h:  
                                angles.append(angle)
                                
                        except:
                            continue
                
                if angles:
                
                    fine_angle = np.median(angles)
                    
            
                    if abs(fine_angle) > 0.2:
                        height, width = image.shape[:2]
                        center = (width // 2, height // 2)
                        
                        rotation_matrix = cv2.getRotationMatrix2D(center, fine_angle, 1.0)
                        
                        fine_tuned = cv2.warpAffine(image, rotation_matrix, (width, height),
                                                   flags=cv2.INTER_CUBIC,
                                                   borderMode=cv2.BORDER_REPLICATE)
                        
                        logger.debug(f"Fine rotation tuning: {fine_angle:.2f} degrees")
                        return fine_tuned
            
            return image
            
        except Exception as e:
            logger.warning(f"Fine rotation tuning failed: {e}")
            return image
    
    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image specifically for YOLO detection.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image optimized for object detection
        """
        try:
            processed = image.copy()
            
        
            target_size = 640
            height, width = processed.shape[:2]
            
            if max(height, width) != target_size:
                scale = target_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                processed = cv2.resize(processed, (new_width, new_height), 
                                     interpolation=cv2.INTER_LINEAR)
            
            
            if processed.shape[0] != processed.shape[1]:
                processed = self._pad_to_square(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Detection preprocessing failed: {e}")
            return image
    
    def _pad_to_square(self, image: np.ndarray, color: Tuple[int, int, int] = (114, 114, 114)) -> np.ndarray:
        """Pad image to square shape."""
        try:
            height, width = image.shape[:2]
            max_dim = max(height, width)
            

            pad_top = (max_dim - height) // 2
            pad_bottom = max_dim - height - pad_top
            pad_left = (max_dim - width) // 2
            pad_right = max_dim - width - pad_left
            
            # Apply padding
            if len(image.shape) == 3:
                padded = cv2.copyMakeBorder(image, pad_top, pad_bottom, pad_left, pad_right,
                                          cv2.BORDER_CONSTANT, value=color)
            else:
                padded = cv2.copyMakeBorder(image, pad_top, pad_bottom, pad_left, pad_right,
                                          cv2.BORDER_CONSTANT, value=color[0])
            
            return padded
            
        except Exception as e:
            logger.error(f"Image padding failed: {e}")
            return image