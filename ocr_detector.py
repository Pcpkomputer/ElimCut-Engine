import easyocr
import cv2
import numpy as np
import re
import os

class OCRDetector:
    def __init__(self, keywords=None):
        if keywords is None:
            keywords = ["eliminated", "knocked out"]
        self.keywords = keywords
        print("Initializing EasyOCR (this may take a moment)...")
        # Initialize easyocr reader for english using local pre-packaged models
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        self.reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=model_dir, download_enabled=False)
        print("EasyOCR initialized.")
        
    def detect_elimination(self, frame):
        """
        Detects if an elimination happened in the given frame and returns the username.
        """
        # Standardize resolution to 1920x1080 for consistent ROI cropping
        frame = cv2.resize(frame, (1920, 1080))
        height, width, _ = frame.shape
        
        # Crop to the bottom middle region where elimination text appears
        # Synchronized with the user's tweaked values
        y_start = int(height * 0.70)
        y_end = int(height * 0.80)
        x_start = int(width * 0.35)
        x_end = int(width * 0.60)
        
        roi = frame[y_start:y_end, x_start:x_end]
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Upscale slightly for the OCR engine, but keep all anti-aliasing intact!
        processed = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        
        # Run OCR
        results = self.reader.readtext(processed)
        
        # Process results
        text_lines = [res[1] for res in results]
        full_text = " ".join(text_lines)
        # print(f"[DEBUG] EasyOCR read: '{full_text}'")
        
        words_lower = full_text.lower().split()
        
        if not words_lower:
            return {'detected': False, 'username': None}
            
        first_word = words_lower[0]
        
        # Looking for any of the provided keywords anywhere in the text
        for kw in self.keywords:
            kw_lower = kw.lower()
            
            # Generate common OCR misreads (prefixes) for known difficult words
            aliases = [kw_lower]
            if kw_lower == 'knocked':
                aliases.extend(['kn', 'kng', 'knoc'])
            elif kw_lower == 'elimination' or kw_lower == 'eliminated':
                aliases.extend(['el', 'eli', 'elim'])
            
            # Check if the keyword or its alias exists exactly ANYWHERE in the text
            match_found = False
            for alias in aliases:
                if alias in full_text.lower():
                    match_found = True
                    break
                    
            # If no exact match, fallback to our similarity percent algorithm!
            if not match_found:
                import difflib
                # Check each word in the OCR text against the keyword
                for word in words_lower:
                    # If the OCR word is at least 75% similar to the keyword, it's a match!
                    # E.g., 'ZcNo_BinKs' compared to 'ZeNo_BinKs' gives ~90% similarity
                    similarity = difflib.SequenceMatcher(None, kw_lower, word).ratio()
                    if similarity >= 0.75:
                        match_found = True
                        break
                        
            if match_found:
                # Return the exact keyword the user provided so it can be used for the folder name
                return {'detected': True, 'username': kw}
            
        return {'detected': False, 'username': None}
