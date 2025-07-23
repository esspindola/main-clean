"""
Advanced Table Detection Service
Professional table structure detection and analysis
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class TableDetector:
    """
    Advanced table detection using computer vision techniques.
    
    Methods:
    - Morphological operations for line detection
    - Contour analysis for table boundary detection
    - Cell structure analysis
    - Table validation and filtering
    """
    
    def __init__(self):
        self.min_table_area = 1000  # Minimum area for valid table
        self.line_thickness_range = (1, 5)  # Valid line thickness range
        logger.info("TableDetector initialized")
    
    def detect_tables(self, image: np.ndarray) -> List[Dict]:
        """
        Detect table regions in the image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected table regions with metadata
        """
        try:
            tables = []
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Method 1: Line-based table detection
            line_tables = self._detect_tables_by_lines(gray)
            tables.extend(line_tables)
            
            # Method 2: Contour-based table detection (fallback)
            if not tables:
                contour_tables = self._detect_tables_by_contours(gray)
                tables.extend(contour_tables)
            
            # Method 3: Grid pattern detection
            grid_tables = self._detect_grid_patterns(gray)
            tables.extend(grid_tables)
            
            # Filter and validate tables
            validated_tables = self._validate_tables(tables, image.shape)
            
            logger.info(f"Detected {len(validated_tables)} valid tables")
            return validated_tables
            
        except Exception as e:
            logger.error(f"Table detection failed: {e}")
            return []
    
    def _detect_tables_by_lines(self, gray_image: np.ndarray) -> List[Dict]:
        """Detect tables using horizontal and vertical line detection."""
        try:
            tables = []
            
            # Apply threshold
            thresh = cv2.adaptiveThreshold(
                gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, -2
            )
            
            # Define morphological kernels for line detection
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
            horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)
            
            # Detect vertical lines
            vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
            vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)
            
            # Combine horizontal and vertical lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            table_mask = cv2.dilate(table_mask, None, iterations=2)
            
            # Find table contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Filter by size and aspect ratio
                if area > self.min_table_area and w > h:  # Tables are typically wider than tall
                    table_info = {
                        'bbox': (x, y, w, h),
                        'area': area,
                        'confidence': self._calculate_table_confidence(
                            gray_image[y:y+h, x:x+w], horizontal_lines[y:y+h, x:x+w], 
                            vertical_lines[y:y+h, x:x+w]
                        ),
                        'method': 'lines',
                        'structure': self._analyze_table_structure(gray_image[y:y+h, x:x+w])
                    }
                    
                    tables.append(table_info)
            
            logger.debug(f"Line-based detection found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Line-based table detection failed: {e}")
            return []
    
    def _detect_tables_by_contours(self, gray_image: np.ndarray) -> List[Dict]:
        """Detect tables using contour analysis."""
        try:
            tables = []
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # Apply threshold
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter contours by area
                area = cv2.contourArea(contour)
                
                if area > self.min_table_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check if contour is rectangular (table-like)
                    aspect_ratio = w / h
                    extent = area / (w * h)
                    
                    if 1.2 < aspect_ratio < 10 and extent > 0.7:  # Table-like properties
                        table_info = {
                            'bbox': (x, y, w, h),
                            'area': area,
                            'confidence': min(extent, aspect_ratio / 10),
                            'method': 'contours',
                            'structure': self._analyze_table_structure(gray_image[y:y+h, x:x+w])
                        }
                        
                        tables.append(table_info)
            
            logger.debug(f"Contour-based detection found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Contour-based table detection failed: {e}")
            return []
    
    def _detect_grid_patterns(self, gray_image: np.ndarray) -> List[Dict]:
        """Detect tables using grid pattern analysis."""
        try:
            tables = []
            
            # Apply edge detection
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                # Separate horizontal and vertical lines
                horizontal_lines = []
                vertical_lines = []
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    
                    # Calculate angle
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    
                    if abs(angle) < 10 or abs(angle) > 170:  # Horizontal
                        horizontal_lines.append(line[0])
                    elif abs(abs(angle) - 90) < 10:  # Vertical
                        vertical_lines.append(line[0])
                
                # Find intersections to identify potential table regions
                intersections = self._find_line_intersections(horizontal_lines, vertical_lines)
                
                # Group intersections into table regions
                table_regions = self._group_intersections_to_tables(intersections, gray_image.shape)
                
                for region in table_regions:
                    x, y, w, h = region['bbox']
                    area = w * h
                    
                    if area > self.min_table_area:
                        table_info = {
                            'bbox': (x, y, w, h),
                            'area': area,
                            'confidence': region['confidence'],
                            'method': 'grid',
                            'structure': self._analyze_table_structure(gray_image[y:y+h, x:x+w])
                        }
                        
                        tables.append(table_info)
            
            logger.debug(f"Grid-based detection found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Grid-based table detection failed: {e}")
            return []
    
    def _calculate_table_confidence(self, table_region: np.ndarray, 
                                   h_lines: np.ndarray, v_lines: np.ndarray) -> float:
        """Calculate confidence score for detected table."""
        try:
            
            factors = []
            
            # Factor 1: Line density
            h_line_density = np.sum(h_lines > 0) / h_lines.size
            v_line_density = np.sum(v_lines > 0) / v_lines.size
            line_density_score = (h_line_density + v_line_density) / 2
            factors.append(min(line_density_score * 10, 1.0))
            
            
            regularity_score = self._calculate_line_regularity(h_lines, v_lines)
            factors.append(regularity_score)
        
            structure_score = self._calculate_rectangular_score(table_region)
            factors.append(structure_score)
            

            confidence = np.mean(factors)
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _analyze_table_structure(self, table_region: np.ndarray) -> Dict:
        """Analyze the internal structure of a detected table."""
        try:
            structure = {
                'estimated_rows': 0,
                'estimated_cols': 0,
                'cell_regularity': 0.0,
                'has_headers': False
            }
            
            
            if len(table_region.shape) == 3:
                gray_table = cv2.cvtColor(table_region, cv2.COLOR_BGR2GRAY)
            else:
                gray_table = table_region.copy()
            
    
            h_projection = np.sum(gray_table < 128, axis=1)  
            h_peaks = self._find_projection_peaks(h_projection)
            structure['estimated_rows'] = max(len(h_peaks) - 1, 1)
            
        
            v_projection = np.sum(gray_table < 128, axis=0)
            v_peaks = self._find_projection_peaks(v_projection)
            structure['estimated_cols'] = max(len(v_peaks) - 1, 1)
            
        
            if len(h_peaks) > 1:
                h_spacing = np.diff(h_peaks)
                h_regularity = 1.0 - (np.std(h_spacing) / np.mean(h_spacing)) if np.mean(h_spacing) > 0 else 0
            else:
                h_regularity = 0
            
            if len(v_peaks) > 1:
                v_spacing = np.diff(v_peaks)
                v_regularity = 1.0 - (np.std(v_spacing) / np.mean(v_spacing)) if np.mean(v_spacing) > 0 else 0
            else:
                v_regularity = 0
            
            structure['cell_regularity'] = (h_regularity + v_regularity) / 2
            
        
            if structure['estimated_rows'] > 1:
                top_section = gray_table[:gray_table.shape[0]//structure['estimated_rows']]
                avg_intensity = np.mean(top_section)
                structure['has_headers'] = avg_intensity < np.mean(gray_table) * 0.9
            
            return structure
            
        except Exception as e:
            logger.warning(f"Table structure analysis failed: {e}")
            return {'estimated_rows': 1, 'estimated_cols': 1, 'cell_regularity': 0.0, 'has_headers': False}
    
    def _find_projection_peaks(self, projection: np.ndarray, min_height: float = 0.1) -> List[int]:
        """Find peaks in projection profile."""
        try:
        
            if np.max(projection) > 0:
                normalized = projection / np.max(projection)
            else:
                return []
            
            # Find peaks
            peaks = []
            threshold = min_height
            
            for i in range(1, len(normalized) - 1):
                if (normalized[i] > normalized[i-1] and 
                    normalized[i] > normalized[i+1] and 
                    normalized[i] > threshold):
                    peaks.append(i)
            
            return peaks
            
        except Exception as e:
            logger.warning(f"Peak finding failed: {e}")
            return []
    
    def _validate_tables(self, tables: List[Dict], image_shape: Tuple) -> List[Dict]:
        """Validate detected tables and remove false positives."""
        try:
            validated = []
            
            for table in tables:
                x, y, w, h = table['bbox']
                
        
                if x < 0 or y < 0 or x + w > image_shape[1] or y + h > image_shape[0]:
                    continue
                
        
                if w < 100 or h < 50:
                    continue
                
        
                aspect_ratio = w / h
                if aspect_ratio < 1.2 or aspect_ratio > 20:
                    continue
                
        
                if table.get('confidence', 0) < 0.3:
                    continue
                
        
                structure = table.get('structure', {})
                if (structure.get('estimated_rows', 0) < 1 or 
                    structure.get('estimated_cols', 0) < 1):
                    continue
                
                validated.append(table)
            
        
            final_tables = self._remove_overlapping_tables(validated)
            
            logger.debug(f"Validated {len(final_tables)} tables from {len(tables)} candidates")
            return final_tables
            
        except Exception as e:
            logger.error(f"Table validation failed: {e}")
            return tables
    
    def _remove_overlapping_tables(self, tables: List[Dict]) -> List[Dict]:
        """Remove overlapping table detections."""
        try:
            if len(tables) <= 1:
                return tables
            
        
            sorted_tables = sorted(tables, key=lambda t: t.get('confidence', 0), reverse=True)
            
            final_tables = []
            
            for table in sorted_tables:
                x1, y1, w1, h1 = table['bbox']
                
            
                overlaps = False
                
                for accepted_table in final_tables:
                    x2, y2, w2, h2 = accepted_table['bbox']
                    
                
                    ix1 = max(x1, x2)
                    iy1 = max(y1, y2)
                    ix2 = min(x1 + w1, x2 + w2)
                    iy2 = min(y1 + h1, y2 + h2)
                    
                    if ix1 < ix2 and iy1 < iy2:
                        intersection_area = (ix2 - ix1) * (iy2 - iy1)
                        table_area = w1 * h1
                        overlap_ratio = intersection_area / table_area
                        
                        if overlap_ratio > 0.5: 
                            overlaps = True
                            break
                
                if not overlaps:
                    final_tables.append(table)
            
            return final_tables
            
        except Exception as e:
            logger.warning(f"Overlap removal failed: {e}")
            return tables
    
    def _find_line_intersections(self, h_lines: List, v_lines: List) -> List[Tuple[int, int]]:
        """Find intersections between horizontal and vertical lines."""
        intersections = []
        
        for h_line in h_lines:
            hx1, hy1, hx2, hy2 = h_line
            
            for v_line in v_lines:
                vx1, vy1, vx2, vy2 = v_line
                
        
                if (min(hx1, hx2) <= max(vx1, vx2) and max(hx1, hx2) >= min(vx1, vx2) and
                    min(hy1, hy2) <= max(vy1, vy2) and max(hy1, hy2) >= min(vy1, vy2)):
                    
                
                    ix = (min(hx1, hx2) + max(hx1, hx2)) // 2
                    iy = (min(vy1, vy2) + max(vy1, vy2)) // 2
                    
                    intersections.append((ix, iy))
        
        return intersections
    
    def _group_intersections_to_tables(self, intersections: List[Tuple[int, int]], 
                                     image_shape: Tuple) -> List[Dict]:
        """Group intersection points into potential table regions."""
        if len(intersections) < 4:  
            return []
        
    
        tables = []
        

        if intersections:
            xs = [p[0] for p in intersections]
            ys = [p[1] for p in intersections]
            
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
    
            w = max_x - min_x
            h = max_y - min_y
            
            if w > 100 and h > 50:  
                confidence = min(len(intersections) / 10, 1.0)  
                
                tables.append({
                    'bbox': (min_x, min_y, w, h),
                    'confidence': confidence
                })
        
        return tables
    
    def _calculate_line_regularity(self, h_lines: np.ndarray, v_lines: np.ndarray) -> float:
        """Calculate regularity score based on line spacing."""
        try:
        
            h_density = np.sum(h_lines > 0) / h_lines.size if h_lines.size > 0 else 0
            v_density = np.sum(v_lines > 0) / v_lines.size if v_lines.size > 0 else 0
            
            return min((h_density + v_density) / 2 * 5, 1.0)
            
        except:
            return 0.5
    
    def _calculate_rectangular_score(self, region: np.ndarray) -> float:
        """Calculate how rectangular a region appears."""
        try:
            # Convert to binary
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            else:
                gray = region.copy()
            
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find largest contour
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate extent (ratio of contour area to bounding box area)
                area = cv2.contourArea(largest_contour)
                x, y, w, h = cv2.boundingRect(largest_contour)
                extent = area / (w * h) if w > 0 and h > 0 else 0
                
                return extent
            
            return 0.5
            
        except:
            return 0.5