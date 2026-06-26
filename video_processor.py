import cv2
import os
from ocr_detector import OCRDetector
from cutter import cut_video

def process_video(video_path, output_dir, keywords=None, pad_before=1.5, pad_after=1.5):
    print(f"Opening video {video_path}...")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"FPS: {fps}, Total Frames: {total_frames}")
    
    detector = OCRDetector(keywords)
    
    eliminations = []
    
    # Process every Nth frame to save time (e.g., check twice a second)
    frame_skip = int(fps / 2) if fps > 0 else 15
    
    current_frame = 0
    while True:
        # Skip frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        if not ret:
            break
            
        timestamp_sec = current_frame / fps
        
        # Check for elimination text
        result = detector.detect_elimination(frame)
        
        if result['detected']:
            username = result['username']
            print(f"[{timestamp_sec:.2f}s] Detected elimination: {username}")
            
            # Simple bot check (we can refine this later)
            is_bot = _is_likely_bot(username)
            category = "bots" if is_bot else "players"
            
            # Record elimination
            eliminations.append({
                'timestamp': timestamp_sec,
                'username': username,
                'category': category
            })
            
            # Skip forward to avoid detecting the same elimination multiple times (e.g., skip 1.5 seconds)
            current_frame += int(fps * 2.5)
            continue
            
        current_frame += frame_skip
        
        # Print progress
        if current_frame % (fps * 60) < frame_skip:
            print(f"Processed {current_frame}/{total_frames} frames ({current_frame/total_frames*100:.1f}%)")
            
    cap.release()
    print(f"Found {len(eliminations)} eliminations.")
    
    # Cut videos
    for elim in eliminations:
        cut_video(video_path, output_dir, elim['timestamp'], elim['username'], elim['category'], pad_before, pad_after)
        
def _is_likely_bot(username):
    # Very basic bot heuristic: Anonymous or contains numbers at the end like Name12
    if "Anonymous" in username:
        return True
    
    # Check if ends with digits (common for Fortnite bots like WordWord12)
    has_digits = any(char.isdigit() for char in username[-2:])
    # For now, default everything to players unless it's anonymous or ends with digits
    if has_digits:
        return True
        
    return False
