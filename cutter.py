import os
try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip

def cut_video(video_path, output_base_dir, timestamp_sec, username, category, pad_before=1.5, pad_after=1.5):
    """
    Cuts the video around the specified timestamp.
    Saves it to output_base_dir/category/username/clip.mp4
    """
    print(f"Cutting video for {username} at {timestamp_sec}s...")
    
    start_time = max(0, timestamp_sec - pad_before)
    end_time = timestamp_sec + pad_after
    
    # Ensure the base output directory exists
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Save all clips in one folder, including category and username in the filename
    output_filename = os.path.join(output_base_dir, f"{category}_{username}_{int(timestamp_sec)}.mp4")
    
    try:
        # Load video
        clip = VideoFileClip(video_path)
        
        # Ensure we don't go past the end of the video
        end_time = min(end_time, clip.duration)
        
        # Cut (support both moviepy v1 and v2)
        try:
            subclip = clip.subclipped(start_time, end_time) # v2
        except AttributeError:
            subclip = clip.subclip(start_time, end_time) # v1
        
        # Write to file
        # logger=None to suppress moviepy output in terminal
        subclip.write_videofile(output_filename, codec="libx264", audio_codec="aac", logger=None)
        
        # Close clip to free resources
        clip.close()
        subclip.close()
        
        print(f"Saved clip to {output_filename}")
        
    except Exception as e:
        print(f"Error cutting video for {username}: {e}")
