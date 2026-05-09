from ultralytics import YOLO
import cv2
from qrdet import QRDetector
import numpy as np
from pathlib import Path
import os
import random
from qreader import QReader
from pylibdmtx.pylibdmtx import encode
from PIL import Image

from pylibdmtx.pylibdmtx import decode

def process_all_qr_codes1(input_dir, output_dir=None, save_crops=True):
    """
    Detect, draw, and save cropped QR codes from all JPG images
    
    Args:
        input_dir: Path to directory containing JPG images
        output_dir: Path to save results (optional, creates 'qr_detections' folder)
        save_crops: Boolean - whether to save cropped QR code images (default: True)
    """
    # Create output directories
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'qr_detections')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectory for cropped QR codes
    if save_crops:
        crops_dir = os.path.join(output_dir, 'cropped_qrs')
        os.makedirs(crops_dir, exist_ok=True)
    
    # Initialize detector
    detector = QRDetector(model_size='n')
    
    # Get all JPG files
    image_extensions = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(input_dir).glob(ext))
    
    print(f"Found {len(image_files)} image(s) to process")
    print("="*60)
    
    # Statistics
    total_qr_count = 0
    processed_files = 0

    crops_names = []
    
    # Process each image
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {img_path.name}")
        
        # Read image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ❌ Failed to read image")
            continue
        
        # Detect QR codes
        detections = detector.detect(img, is_bgr=True)
        
        if not detections:
            print(f"  ⚠️ No QR codes found")
            annotated = img.copy()
            cv2.putText(annotated, "No QR codes found", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            print(f"  ✅ Found {len(detections)} QR code(s)")
            total_qr_count += len(detections)
            
            # Draw detections
            annotated = img.copy()
            for j, detection in enumerate(detections, 1):
                x1, y1, x2, y2 = [int(coord) for coord in detection['bbox_xyxy']]
                confidence = detection['confidence']
                
                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # Draw label
                label = f"QR {j} ({confidence:.2f})"
                cv2.putText(annotated, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                print(f"    QR {j}: confidence={confidence:.2f}, bbox=({x1},{y1},{x2},{y2})")
                
                # SAVE CROPPED QR CODE
                if save_crops:
                    # Extract crop region (add small padding for safety)
                    padding = 5
                    crop_x1 = max(0, x1 - padding)
                    crop_y1 = max(0, y1 - padding)
                    crop_x2 = min(img.shape[1], x2 + padding)
                    crop_y2 = min(img.shape[0], y2 + padding)
                    
                    # Crop the image
                    cropped_qr = img[crop_y1:crop_y2, crop_x1:crop_x2]
                    
                    # Generate unique filename for the crop
                    original_name = Path(img_path).stem
                    crop_filename = f"{original_name}_qr{j}.jpg"
                    crop_path = os.path.join(crops_dir, crop_filename)
                    
                    # Save cropped QR
                    cv2.imwrite(crop_path, cropped_qr)
                    print(f"      💾 Cropped QR saved: {crop_filename}")
                    crops_names.append(crop_path)
        
        # Save annotated image
        output_path = os.path.join(output_dir, f"detected_{img_path.name}")
        cv2.imwrite(output_path, annotated)
        print(f"  💾 Annotated image saved: {output_path}")
        processed_files += 1
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PROCESSING SUMMARY")
    print("="*60)
    print(f"✅ Processed files: {processed_files}/{len(image_files)}")
    print(f"✅ Total QR codes found: {total_qr_count}")
    print(f"✅ Results saved to: {output_dir}")
    if save_crops:
        print(f"✅ Cropped QR codes saved to: {crops_dir}")
    
    return {
        'processed_files': processed_files,
        'total_qr_codes': total_qr_count,
        'output_dir': output_dir,
        'crops_dir': crops_dir if save_crops else None,
        'cropped': crops_names,
    }


def detect():
    # Usage
    return process_all_qr_codes1(
        input_dir='data/qr_dataset_handmade_v0/images',
        output_dir=None,  # Will create 'qr_detections' subfolder
        save_crops=True
    )

def decode1(cropped):
    for f in cropped:
        image = cv2.imread(f)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Get current dimensions
        h, w = gray.shape
        
        # Resize so that minimum dimension becomes 200
        min_dim = min(h, w)
        if min_dim < 200:
            scale = 200 / min_dim
            new_w = int(w * scale)
            new_h = int(h * scale)
            resized = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        else:
            resized = gray

        # No need rotate iteration
        results = decode(resized, shrink=3, max_count=1)
        for result in results:
            data = result.data.decode('utf-8')
            print(f"Decoded data: {data}, for: {f}")

            # TODO() Doesn't work. Image is junk
            if 0:
                # Generate DataMatrix
                encoded = encode("(01)08700216351546(21)5Ke8Jn(93)v4fm".encode('utf-8'))

                img = Image.frombytes('L', (encoded.width, encoded.height), encoded.pixels)
                
                img.save('datamatrix_code.png')
                break

def main():
    result = detect()
    cropped = result['cropped']
    decode1(cropped)


if __name__ == "__main__":
    main()