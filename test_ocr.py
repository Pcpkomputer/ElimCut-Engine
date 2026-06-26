import cv2
import sys
import argparse
import numpy as np
from ocr_detector import OCRDetector

def main():
    parser = argparse.ArgumentParser(description="Test OCR cropping on a single image")
    parser.add_argument("--image", required=True, help="Path to the test image")
    parser.add_argument("--keywords", default="eliminated,knocked out", help="Comma-separated keywords to detect")
    args = parser.parse_args()

    image_path = args.image
    keywords = [k.strip().lower() for k in args.keywords.split(",")]
    frame = cv2.imread(image_path)
    
    if frame is None:
        print(f"Error: Failed to load image at {image_path}")
        sys.exit(1)

    print("Original resolution:", frame.shape)
    print("Resizing frame to 1920x1080 for consistent testing...")
    
    # Standardize resolution (must match what's in ocr_detector.py)
    frame = cv2.resize(frame, (1920, 1080))
    height, width, _ = frame.shape

    # Replicate the cropping logic to show you visually what is being passed to OCR
    y_start = int(height * 0.70)
    y_end = int(height * 0.80)
    x_start = int(width * 0.35)
    x_end = int(width * 0.60)
    roi = frame[y_start:y_end, x_start:x_end]

    # Save the cropped region so you can manually inspect if it covers the text well
    crop_filename = "test_roi_crop.jpg"
    cv2.imwrite(crop_filename, roi)
    print(f"Saved cropped region to {crop_filename} for visual inspection.")

    # Keep all natural anti-aliasing and just upscale for the OCR engine
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    processed = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    processed_filename = "test_processed_crop.jpg"
    cv2.imwrite(processed_filename, processed)
    print(f"Saved preprocessed region to {processed_filename} for visual inspection.")

    print("\nRunning OCR Detector...")
    detector = OCRDetector(keywords)
    result = detector.detect_elimination(frame)
    
    print("\n====================")
    print(f"OCR Result: {result}")
    print("====================")

if __name__ == "__main__":
    main()
