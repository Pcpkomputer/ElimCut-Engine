import argparse
import sys
import os
from video_processor import process_video

def main():
    parser = argparse.ArgumentParser(description="ElimCut Engine - Fortnite Elimination Cutter")
    parser.add_argument("--video", required=True, help="Path to the input video file")
    parser.add_argument("--out", required=True, help="Path to the output directory")
    parser.add_argument("--keywords", default="eliminated,knocked out", help="Comma-separated list of keywords to trigger elimination")
    parser.add_argument("--pad_before", type=float, default=1.5, help="Seconds before the elimination to cut")
    parser.add_argument("--pad_after", type=float, default=1.5, help="Seconds after the elimination to cut")
    
    args = parser.parse_args()
    
    video_path = args.video
    output_dir = args.out
    pad_before = args.pad_before
    pad_after = args.pad_after
    keywords = [k.strip().lower() for k in args.keywords.split(",")]
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        sys.exit(1)
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    print(f"Starting processing for video: {video_path}")
    print(f"Output directory: {output_dir}")
    print(f"Keywords: {keywords}")
    print(f"Padding: -{pad_before}s / +{pad_after}s")
    
    process_video(video_path, output_dir, keywords, pad_before, pad_after)
    
    print("Processing completed successfully.")

if __name__ == "__main__":
    main()
