import os
import json
from PIL import Image
import glob
import argparse

def convert_to_coco(images_dir, labels_dir, output_file):
    """
    Convert YOLO format annotations to COCO format for the AppleBBCH81 dataset.
    
    Args:
        images_dir (str): Directory containing the image files
        labels_dir (str): Directory containing the YOLO format label files
        output_file (str): Path to save the COCO format JSON file
    """
    # Initialize COCO format
    coco_format = {
        "info": {
            "description": "AppleBBCH76 Dataset - Apple fruit images for object detection",
            "version": "1.0",
            "year": 2024,
            "contributor": "Project LZP",
            "date_created": "2024/04/12",
            "url": "https://www.kaggle.com/datasets/projectlzp201910094/applebbch76"
        },
        "licenses": [
            {
                "id": 1,
                "name": "CC BY 4.0",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }
        ],
        "images": [],
        "annotations": [],
        "categories": [
            {
                "id": 0,
                "name": "apple",
                "supercategory": "fruit"
            }
        ]
    }
    
    # Get all image files
    image_files = sorted(glob.glob(os.path.join(images_dir, "*.jpg")))
    annotation_id = 1
    
    print(f"Found {len(image_files)} images in {images_dir}")
    
    for img_id, img_path in enumerate(image_files, 1):
        # Get image info
        img = Image.open(img_path)
        width, height = img.size
        
        # Add image info to COCO format
        img_filename = os.path.basename(img_path)
        coco_format["images"].append({
            "id": img_id,
            "license": 1,
            "file_name": img_filename,
            "height": height,
            "width": width,
            "date_captured": "2024-04-12"
        })
        
        # Get corresponding label file
        label_path = os.path.join(labels_dir, os.path.splitext(img_filename)[0] + ".txt")
        if not os.path.exists(label_path):
            print(f"Warning: No label file found for {img_filename}")
            continue
            
        # Read and convert annotations
        with open(label_path, 'r') as f:
            for line in f:
                try:
                    class_id, x_center, y_center, w, h = map(float, line.strip().split())
                    
                    # Convert YOLO format to COCO format (x, y, width, height)
                    x = (x_center - w/2) * width
                    y = (y_center - h/2) * height
                    w = w * width
                    h = h * height
                    
                    # Add annotation to COCO format
                    coco_format["annotations"].append({
                        "id": annotation_id,
                        "image_id": img_id,
                        "category_id": int(class_id),
                        "bbox": [x, y, w, h],
                        "area": w * h,
                        "segmentation": [],
                        "iscrowd": 0
                    })
                    annotation_id += 1
                except ValueError as e:
                    print(f"Error parsing line in {label_path}: {line.strip()}. Error: {e}")
    
    # Save to JSON file
    with open(output_file, 'w') as f:
        json.dump(coco_format, f, indent=2)
    
    print(f"Conversion complete. Created {len(coco_format['images'])} image entries and {len(coco_format['annotations'])} annotation entries.")
    print(f"COCO format JSON saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert YOLO format annotations to COCO format for the AppleBBCH81 dataset')
    parser.add_argument('--images', type=str, default="data/images", help='Directory containing the image files')
    parser.add_argument('--labels', type=str, default="data/labels", help='Directory containing the YOLO format label files')
    parser.add_argument('--output', type=str, default="data/data.json", help='Path to save the COCO format JSON file')
    
    args = parser.parse_args()
    
    convert_to_coco(args.images, args.labels, args.output)