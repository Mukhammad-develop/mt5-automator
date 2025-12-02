"""
OCR Processor
Extracts text from trading signal images using OCR with advanced preprocessing
"""
import os
import re
from typing import Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from src.utils import create_class_logger


class OCRProcessor:
    """
    Process images to extract trading signals using OCR
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OCR processor
        
        Args:
            config: Configuration dictionary
        """
        self.logger = create_class_logger('OCRProcessor')
        self.config = config
        self.ocr_config = config.get('ocr', {})
        
        # Set tesseract command path
        tesseract_cmd = self.ocr_config.get('tesseract_cmd')
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Preprocessing settings
        self.preprocessing = self.ocr_config.get('preprocessing', {})
        self.resize_factor = self.preprocessing.get('resize_factor', 2.0)
        self.contrast_boost = self.preprocessing.get('contrast_boost', True)
        self.denoise = self.preprocessing.get('denoise', True)
        self.sharpen = self.preprocessing.get('sharpen', True)
        
        self.logger.info("OCRProcessor initialized")
    
    def process_image(self, image_path: str) -> Optional[str]:
        """
        Process image and extract text using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text or None if failed
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Image not found: {image_path}")
                return None
            
            self.logger.info(f"Processing image: {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            self.logger.debug(f"Image size: {image.shape[1]}x{image.shape[0]}")
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = self._extract_text(processed_image)
            
            # Post-process text
            cleaned_text = self._postprocess_text(text)
            
            self.logger.info(f"Extracted text ({len(cleaned_text)} chars)")
            self.logger.debug(f"Text: {cleaned_text[:200]}")
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Error processing image: {e}", exc_info=True)
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing pipeline to improve OCR accuracy
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to PIL Image for some operations
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 1. Resize (upscale for small images)
            if self.resize_factor > 1.0:
                new_width = int(pil_image.width * self.resize_factor)
                new_height = int(pil_image.height * self.resize_factor)
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                self.logger.debug(f"Resized to {new_width}x{new_height}")
            
            # 2. Contrast boost
            if self.contrast_boost:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(1.5)
                self.logger.debug("Applied contrast boost")
            
            # 3. Convert to grayscale
            pil_image = pil_image.convert('L')
            
            # Convert back to OpenCV format
            image = np.array(pil_image)
            
            # 4. Denoise
            if self.denoise:
                image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
                self.logger.debug("Applied denoising")
            
            # 5. Adaptive thresholding (works better than simple thresholding)
            image = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            self.logger.debug("Applied adaptive thresholding")
            
            # 6. Sharpen
            if self.sharpen:
                kernel = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
                image = cv2.filter2D(image, -1, kernel)
                self.logger.debug("Applied sharpening")
            
            # 7. Morphological operations to remove noise
            kernel = np.ones((2, 2), np.uint8)
            image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error in preprocessing: {e}")
            return image
    
    def _extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from preprocessed image using Tesseract
        
        Args:
            image: Preprocessed image
            
        Returns:
            Extracted text
        """
        try:
            # Tesseract configuration
            # --psm 6: Assume uniform block of text
            # --oem 3: Use default OCR engine mode
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error in text extraction: {e}")
            return ""
    
    def _postprocess_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw OCR output
            
        Returns:
            Cleaned text
        """
        try:
            # Remove null characters
            text = text.replace('\x00', '')
            
            # Fix common OCR mistakes
            replacements = {
                'O': '0',  # Letter O to zero (in number context)
                'o': '0',  # Letter o to zero (in number context)
                'l': '1',  # Letter l to one (in number context)
                'I': '1',  # Letter I to one (in number context)
                'S': '5',  # Letter S to five (in number context)
                'B': '8',  # Letter B to eight (in number context)
                '|': '1',  # Pipe to one
                '!': '1',  # Exclamation to one
            }
            
            # Apply replacements carefully (only in number contexts)
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Check if line contains price/number patterns
                if re.search(r'\d', line) or any(keyword in line.upper() for keyword in ['BUY', 'SELL', 'TP', 'SL']):
                    # Apply replacements for this line
                    for old, new in replacements.items():
                        # Only replace in number contexts (before/after digits or decimal points)
                        line = re.sub(f'(?<=\\d){old}', new, line)
                        line = re.sub(f'{old}(?=\\d)', new, line)
                        line = re.sub(f'(?<=\\.){old}', new, line)
                        line = re.sub(f'{old}(?=\\.)', new, line)
                
                cleaned_lines.append(line)
            
            text = '\n'.join(cleaned_lines)
            
            # Remove excessive whitespace
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\n\s*\n', '\n', text)
            
            # Trim
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error in postprocessing: {e}")
            return text
    
    def extract_numbers(self, text: str) -> list:
        """
        Extract all numbers from text (useful for debugging)
        
        Args:
            text: Text to extract from
            
        Returns:
            List of numbers found
        """
        # Find all numbers (including decimals)
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) for n in numbers if n]
    
    def save_preprocessed_image(self, image_path: str, output_path: str = None):
        """
        Save preprocessed image for debugging
        
        Args:
            image_path: Input image path
            output_path: Output path (default: adds _processed suffix)
        """
        try:
            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_processed{ext}"
            
            # Load and preprocess
            image = cv2.imread(image_path)
            processed = self._preprocess_image(image)
            
            # Save
            cv2.imwrite(output_path, processed)
            self.logger.info(f"Saved preprocessed image: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving preprocessed image: {e}")


def main():
    """
    Test OCR processor
    """
    from src.utils import load_config, setup_logging
    
    # Load config
    config = load_config()
    logger = setup_logging(config)
    
    # Create processor
    processor = OCRProcessor(config)
    
    # Test with sample image (if exists)
    test_image = 'data/images/test_signal.jpg'
    if os.path.exists(test_image):
        text = processor.process_image(test_image)
        logger.info(f"Extracted text:\n{text}")
        
        # Extract numbers
        numbers = processor.extract_numbers(text)
        logger.info(f"Numbers found: {numbers}")
        
        # Save preprocessed image
        processor.save_preprocessed_image(test_image)
    else:
        logger.warning(f"Test image not found: {test_image}")
        logger.info("Place a test image at data/images/test_signal.jpg to test OCR")


if __name__ == '__main__':
    main()

