# AppleBBCH76 Dataset

A dataset of apple fruit images captured in apple orchards, designed for object detection tasks using YOLO architecture.

## Dataset Description

The AppleBBCH76 dataset is designed for apple fruit detection tasks. It contains annotated photographs of apple orchards, making it suitable for computer vision, object detection, and deep learning research in agricultural applications.

- **Number of classes**: 1 (Apple fruits)
- **Image format**: YOLO format, JSON format
- **Image size**: 640x640 pixels
- **Total images**: 76
- **Total annotations**: 76

## Dataset Structure

The dataset includes:
- Annotated images (640x640)
- YOLO format annotation files (`.txt`)
- JSON format annotation files (`.json`)
- Single class annotations for apple fruits
- Training and validation splits

目录结构示例：
```
data/
  images/
    *.jpg         # 图像文件
    *.json        # 每张图片对应的标注文件
  labels/
    *.txt         # YOLO格式的标签文件
  data.json       # 汇总所有标注的大型JSON文件
```

## Annotation Format

### 1. YOLO Label Format

每张图片对应一个`.txt`标签文件，每一行为一个目标，格式如下：

```
<class_id> <center_x> <center_y> <width> <height>
```
- `class_id`：类别编号（本数据集均为0，表示苹果）
- `center_x`、`center_y`：目标中心点的归一化坐标（相对于图像宽高，范围0~1）
- `width`、`height`：目标的归一化宽高（相对于图像宽高，范围0~1）

示例：
```
0 0.568249 0.686189 0.094073 0.100357
```

### 2. JSON Annotation Format

每张图片有一个对应的`.json`标注文件，结构如下：

```json
{
  "info": {
    "description": "data",
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
      "id": 8220686386,
      "width": 640,
      "height": 640,
      "file_name": "DSC_1379_17kv4r33k_9.jpg",
      "size": 75949,
      "format": "JPEG",
      "url": "",
      "hash": "",
      "status": "success"
    }
  ],
  "annotations": [
    {
      "id": 8744821386,
      "image_id": 8220686386,
      "category_id": 3402171386,
      "segmentation": [],
      "area": 3840,
      "bbox": [333, 407, 60, 64]
    }
    // ... more objects
  ],
  "categories": [
    {
      "id": 3402171386,
      "name": "AppleBBCH76",
      "supercategory": "apple"
    }
  ]
}
```
- `images`：图片信息，包括id、尺寸、文件名等
- `annotations`：目标标注，每个目标包含id、所属图片id、类别id、分割信息（为空）、面积、边界框（左上角x, y, 宽, 高）
- `categories`：类别信息

## Applications

This dataset can be used for:
- Apple fruit detection
- Object detection
- Computer vision research
- Deep learning model training
- Agricultural AI applications
- Precision agriculture

## Categories

- Computer Science
- Artificial Intelligence
- Computer Vision
- Object Detection
- Machine Learning
- Agriculture
- Deep Learning
- Precision Agriculture

## Citation

```
[Citation information to be added when available]
```

## License

This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

## Source

The dataset is available at:
- [Kaggle Dataset](https://www.kaggle.com/datasets/projectlzp201910094/applebbch76) 