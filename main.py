#!/usr/bin/env python3
"""
Phone Number Extractor Pipeline

This script extracts phone numbers from a WhatsApp contact list video:
1. Extract frames from video
2. Use Gemini API to extract contacts from each frame
3. Post-process and save unique contacts to CSV
"""

import argparse
import os
import shutil

from extract_images import extract_images
from extract_contacts import extract_contacts
from post_process import post_process


def clean_images():
    """Remove all images from the images folder."""
    if os.path.exists("images"):
        shutil.rmtree("images")
        print("Cleaned images folder")


def main():
    parser = argparse.ArgumentParser(description="Extract phone numbers from WhatsApp contact list video")
    parser.add_argument("video_path", nargs="?", 
                        default="videos/WhatsApp Video 2025-12-01 at 17.27.58.mp4",
                        help="Path to the video file")
    parser.add_argument("--clean", action="store_true", 
                        help="Clean images folder before extracting")
    parser.add_argument("--skip-extract", action="store_true",
                        help="Skip image extraction (use existing images)")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Phone Number Extractor Pipeline")
    print("=" * 50)
    
    # Step 1: Clean if requested
    if args.clean:
        clean_images()
    
    # Step 2: Extract images from video
    if not args.skip_extract:
        print("\n[Step 1/3] Extracting frames from video...")
        frame_count = extract_images(args.video_path)
        if frame_count == 0:
            print("Error: No frames extracted. Check video path.")
            return
    else:
        print("\n[Step 1/3] Skipping image extraction (using existing images)")
    
    # Step 3: Extract contacts using Gemini
    print("\n[Step 2/3] Extracting contacts from images using Gemini API...")
    record_count = extract_contacts()
    
    # Step 4: Post-process and save to CSV
    print("\n[Step 3/3] Post-processing and saving to CSV...")
    unique_count = post_process()
    
    print("\n" + "=" * 50)
    print("Pipeline Complete!")
    print(f"  - Processed {record_count} images")
    print(f"  - Extracted {unique_count} unique phone numbers")
    print(f"  - Output saved to: contacts.csv")
    print("=" * 50)


if __name__ == "__main__":
    main()
