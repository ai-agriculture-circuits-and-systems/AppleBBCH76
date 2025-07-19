import os
import json
import time
import random
from PIL import Image
from datetime import datetime

def generate_unique_id():
    """Generate 10-digit unique code with last 3 digits containing timestamp"""
    # Generate 7 random digits
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    # Get last 3 digits of current timestamp
    timestamp = int(time.time())
    timestamp_part = str(timestamp)[-3:]
    # Combine into 10-digit code
    unique_id = int(random_part + timestamp_part)
    return unique_id

def get_image_dimensions(image_path):
    """Get image width and height"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return 256, 256  # Default size

def read_yolo_annotations(label_path):
    """Read YOLO format annotations from label file"""
    annotations = []
    try:
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        center_x = float(parts[1])
                        center_y = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        annotations.append({
                            'class_id': class_id,
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': width,
                            'height': height
                        })
    except Exception as e:
        print(f"Error reading label file {label_path}: {e}")
    return annotations

def convert_yolo_to_bbox(yolo_annotation, img_width, img_height):
    """Convert YOLO format to bbox format [x, y, width, height]"""
    center_x = yolo_annotation['center_x'] * img_width
    center_y = yolo_annotation['center_y'] * img_height
    width = yolo_annotation['width'] * img_width
    height = yolo_annotation['height'] * img_height
    
    # Convert to [x, y, width, height] format
    x = center_x - width / 2
    y = center_y - height / 2
    
    return [int(x), int(y), int(width), int(height)]

def generate_annotation_json(image_path, label_path, image_id, category_id):
    """Generate annotation JSON for a single image using existing label data"""
    # Get image dimensions
    width, height = get_image_dimensions(image_path)
    
    # Get filename
    file_name = os.path.basename(image_path)
    
    # Get grandparent directory name for description (grandparent folder)
    grandparent_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(image_path))))
    
    # Read YOLO annotations
    yolo_annotations = read_yolo_annotations(label_path)
    
    # Convert annotations to bbox format
    annotations = []
    for i, yolo_ann in enumerate(yolo_annotations):
        bbox = convert_yolo_to_bbox(yolo_ann, width, height)
        area = bbox[2] * bbox[3]  # width * height
        
        # Generate unique annotation ID for each annotation
        annotation_id = generate_unique_id()
        
        annotation = {
            "id": annotation_id,  # Unique ID for each annotation
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": [],
            "area": area,
            "bbox": bbox
        }
        annotations.append(annotation)
    
    annotation_data = {
        "info": {
            "description": grandparent_dir,
            "version": "1.0",
            "year": 2025,
            "contributor": "search engine",
            "source": "augmented",
            "license": {
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }
        },
        "images": [
            {
                "id": image_id,
                "width": width,
                "height": height,
                "file_name": file_name,
                "size": os.path.getsize(image_path),
                "format": "JPEG",
                "url": "",
                "hash": "",
                "status": "success"
            }
        ],
        "annotations": annotations,
        "categories": [
            {"id": category_id, "name": "AppleBBCH76", "supercategory": "apple"}
        ]
    }
    
    return annotation_data

def main():
    # Folder paths
    images_dir = "images"
    labels_dir = "labels"
    
    # Ensure folders exist
    if not os.path.exists(images_dir):
        print(f"Images directory {images_dir} does not exist!")
        return
    
    if not os.path.exists(labels_dir):
        print(f"Labels directory {labels_dir} does not exist!")
        return
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) 
                   if os.path.isfile(os.path.join(images_dir, f)) 
                   and any(f.lower().endswith(ext) for ext in image_extensions)]
    
    # Get all label files
    label_files = [f for f in os.listdir(labels_dir) 
                   if os.path.isfile(os.path.join(labels_dir, f)) 
                   and f.endswith('.txt')]
    
    # Create a mapping of base names to label files
    label_map = {}
    for label_file in label_files:
        base_name = os.path.splitext(label_file)[0]
        label_map[base_name] = label_file
    
    processed_count = 0
    
    # Process each image file
    for image_file in image_files:
        # Get base name without extension
        base_name = os.path.splitext(image_file)[0]
        
        # Check if corresponding label file exists
        if base_name in label_map:
            image_path = os.path.join(images_dir, image_file)
            label_path = os.path.join(labels_dir, label_map[base_name])
            
            print(f"Processing: {image_file} -> {label_map[base_name]}")
            
            # Generate unique IDs
            image_id = generate_unique_id()
            category_id = generate_unique_id()
            
            # Generate annotation JSON
            annotation_json = generate_annotation_json(image_path, label_path, image_id, category_id)
            
            # Generate JSON filename (same name as image but with .json extension)
            json_filename = os.path.splitext(image_file)[0] + ".json"
            json_path = os.path.join(images_dir, json_filename)
            
            # Save JSON file
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(annotation_json, f, indent=2, ensure_ascii=False)
                print(f"Generated annotation: {json_filename}")
                processed_count += 1
            except Exception as e:
                print(f"Error saving JSON for {image_file}: {e}")
        else:
            print(f"No label file found for {image_file}")
    
    print(f"Annotation generation completed! Processed {processed_count} files.")

if __name__ == "__main__":
    main() 