import cv2
import argparse
import sys
import os
from ocr_detector import OCRDetector
from cutter import cut_video

def main():
    parser = argparse.ArgumentParser(description="Test OCR on a video file")
    parser.add_argument("--video", required=True, help="Path to the test video")
    parser.add_argument("--keywords", default="eliminated,knocked", help="Comma-separated keywords")
    parser.add_argument("--output", default="output_clips", help="Folder to save the cut clips")
    parser.add_argument("--pad_before", type=float, default=1.5, help="Seconds before the elimination to cut")
    parser.add_argument("--pad_after", type=float, default=1.5, help="Seconds after the elimination to cut")
    args = parser.parse_args()

    video_path = args.video
    output_dir = args.output
    keywords = [k.strip() for k in args.keywords.split(",")]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        sys.exit(1)
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video loaded: {video_path}")
    print(f"FPS: {fps}, Total Frames: {total_frames}, Duration: {total_frames/fps:.2f}s")
    
    detector = OCRDetector(keywords)
    
    # Process 2 frames per second to save time
    frame_skip = int(fps / 2) if fps > 0 else 15
    current_frame = 0
    
    print("\nScanning video for keywords...")
    
    while current_frame < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        if not ret:
            break
            
        timestamp_sec = current_frame / fps
        
        result = detector.detect_elimination(frame)
        
        if result['detected']:
            keyword_matched = result['username']
            print(f"\n=========================================")
            print(f"🔥 MATCH DETECTED! Timestamp: {timestamp_sec:.2f}s")
            print(f"🔥 Keyword matched: {keyword_matched}")
            print(f"=========================================\n")
            
            # Actually cut the video clip!
            cut_video(video_path, output_dir, timestamp_sec, keyword_matched, "test_clip", args.pad_before, args.pad_after)
            
            # Skip ahead 1.5 seconds so we don't detect the same elimination message multiple times
            current_frame += int(fps * 1.5)
        else:
            # Print a progress indicator without spamming new lines
            sys.stdout.write(f"\rScanning timestamp: {timestamp_sec:.2f}s ")
            sys.stdout.flush()
            current_frame += frame_skip
            
    print("\nDone scanning video!")
    cap.release()

if __name__ == "__main__":
    main()
