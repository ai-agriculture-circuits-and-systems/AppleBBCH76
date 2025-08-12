from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image


# NOTE: This file is intentionally verbose and defensive (similar to
# `datasets/acfr-multifruit-2016/scripts/convert_to_coco.py`) to match the
# standardized style across datasets.


@dataclass(frozen=True)
class CocoImage:
    """COCO "images" entry.

    Attributes:
        id: Unique integer id for the image.
        file_name: Basename of the image file.
        width: Image width in pixels.
        height: Image height in pixels.
        license: License id (defaults to 1: CC BY 4.0).
        date_captured: ISO-like capture date string.
    """

    id: int
    file_name: str
    width: int
    height: int
    license: int = 1
    date_captured: str = "2024-04-12"


@dataclass(frozen=True)
class CocoAnnotation:
    """COCO "annotations" entry (bbox-only).

    Attributes:
        id: Unique integer id for the annotation.
        image_id: Image id that this annotation belongs to.
        category_id: Category id (1 for apples in this dataset).
        bbox: COCO bbox [x, y, width, height] in pixels.
        area: Area in pixels^2.
        iscrowd: Whether this is a crowd region (0 or 1).
        segmentation: Empty list for bbox-only annotations.
    """

    id: int
    image_id: int
    category_id: int
    bbox: List[float]
    area: float
    iscrowd: int = 0
    segmentation: Optional[List[List[float]]] = None  # keep empty list by default


def _read_split_file(path: Path) -> List[str]:
    """Read a split file into a list of image stems.

    Args:
        path: Path to a split file. One image stem per line.

    Returns:
        A list of non-empty, stripped stems. Returns an empty list if not found.
    """

    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _image_size(image_path: Path) -> Tuple[int, int]:
    """Return (width, height) for an image path using PIL.

    Args:
        image_path: Path to an image file.

    Returns:
        Tuple of (width, height) in pixels.
    """

    with Image.open(image_path) as img:
        return img.width, img.height


def _read_yolo_labels(label_path: Path) -> List[Tuple[int, float, float, float, float]]:
    """Parse a YOLO label file.

    Each line is expected to be: class x_center y_center width height (all normalized 0..1).

    Args:
        label_path: Path to a .txt label file.

    Returns:
        A list of tuples (class_id, xc, yc, w, h).
    """

    if not label_path.exists():
        return []
    rows: List[Tuple[int, float, float, float, float]] = []
    for raw in label_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split()
        if len(parts) != 5:
            continue
        try:
            cls = int(float(parts[0]))
            xc = float(parts[1])
            yc = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])
        except ValueError:
            continue
        rows.append((cls, xc, yc, w, h))
    return rows


def _yolo_to_coco_bbox(
    xc: float, yc: float, w: float, h: float, width_px: int, height_px: int
) -> Tuple[float, float, float, float]:
    """Convert YOLO normalized bbox to COCO pixel bbox.

    Args:
        xc: Center x (0..1)
        yc: Center y (0..1)
        w: Width (0..1)
        h: Height (0..1)
        width_px: Image width in pixels
        height_px: Image height in pixels

    Returns:
        (x, y, width, height) in pixels.
    """

    width = w * width_px
    height = h * height_px
    x = (xc * width_px) - (width / 2.0)
    y = (yc * height_px) - (height / 2.0)
    return x, y, width, height


def _build_coco_dict() -> Dict[str, object]:
    """Create a fresh COCO dictionary skeleton for AppleBBCH76."""

    return {
        "info": {
            "description": "AppleBBCH76 Dataset - Apple fruit images for object detection",
            "version": "1.0",
            "year": 2024,
            "contributor": "Project LZP",
            "date_created": "2024-04-12",
            "url": "https://www.kaggle.com/datasets/projectlzp201910094/applebbch76",
        },
        "licenses": [
            {"id": 1, "name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}
        ],
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 1, "name": "apple", "supercategory": "fruit"}
        ],
    }


def _collect_image_paths(images_dir: Path, stems: Optional[Sequence[str]] = None) -> List[Path]:
    """Collect image paths by optional list of stems.

    Args:
        images_dir: Directory containing images.
        stems: Image base names (without extension) to include. If None, include all images.

    Returns:
        List of image paths sorted by name.
    """

    candidates = sorted([p for p in images_dir.glob("*.jpg")])
    if stems is None:
        return candidates
    stem_set = set(stems)
    return [p for p in candidates if p.stem in stem_set]


def convert_to_coco(
    images_dir: Path,
    labels_dir: Path,
    out_json: Path,
    stems: Optional[Sequence[str]] = None,
) -> None:
    """Convert YOLO annotations to COCO JSON for a set of images.

    Args:
        images_dir: Directory with image files.
        labels_dir: Directory with YOLO .txt label files.
        out_json: Output JSON path.
        stems: Optional list of image stems to restrict conversion.
    """

    coco = _build_coco_dict()
    images: List[CocoImage] = []
    annotations: List[CocoAnnotation] = []

    image_paths = _collect_image_paths(images_dir, stems)
    print(f"Found {len(image_paths)} images to convert from {images_dir}")

    next_ann_id = 1
    for img_id, path in enumerate(image_paths, start=1):
        width, height = _image_size(path)
        images.append(
            CocoImage(
                id=img_id,
                file_name=path.name,
                width=width,
                height=height,
            )
        )

        lbl = labels_dir / f"{path.stem}.txt"
        rows = _read_yolo_labels(lbl)
        for cls, xc, yc, w, h in rows:
            # Normalize class id to 1 (apple)
            category_id = 1
            x, y, ww, hh = _yolo_to_coco_bbox(xc, yc, w, h, width, height)
            annotations.append(
                CocoAnnotation(
                    id=next_ann_id,
                    image_id=img_id,
                    category_id=category_id,
                    bbox=[x, y, ww, hh],
                    area=ww * hh,
                    iscrowd=0,
                    segmentation=[],
                )
            )
            next_ann_id += 1

    # Dump
    coco["images"] = [image.__dict__ for image in images]
    coco["annotations"] = [
        {
            "id": ann.id,
            "image_id": ann.image_id,
            "category_id": ann.category_id,
            "bbox": ann.bbox,
            "area": ann.area,
            "iscrowd": ann.iscrowd,
            "segmentation": ann.segmentation if ann.segmentation is not None else [],
        }
        for ann in annotations
    ]

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(coco, indent=2), encoding="utf-8")
    print(
        f"Saved COCO JSON with {len(images)} images and {len(annotations)} annotations to {out_json}"
    )


def main() -> None:
    """CLI entry point.

    Examples:
        python scripts/convert_to_coco.py \
            --images data/images --labels data/labels --out annotations \
            --splits train val test --split-dir sets

        python scripts/convert_to_coco.py \
            --images data/images --labels data/labels --out annotations
    """

    parser = argparse.ArgumentParser(
        description=(
            "Convert YOLO format annotations to COCO format for the AppleBBCH76 dataset"
        )
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("data/images"),
        help="Directory containing the image files",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=Path("data/labels"),
        help="Directory containing the YOLO label files",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("annotations"),
        help="Output directory to save COCO JSON(s)",
    )
    parser.add_argument(
        "--splits",
        nargs="*",
        default=[],
        help="Optional list of splits to export (e.g., train val test). If omitted, exports a single 'all' JSON.",
    )
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("sets"),
        help="Directory containing split files like train.txt, val.txt, test.txt.",
    )

    args = parser.parse_args()

    if args.splits:
        for split in args.splits:
            stems = _read_split_file(args.split_dir / f"{split}.txt")
            out_path = args.out / f"applebbch76_instances_{split}.json"
            convert_to_coco(args.images, args.labels, out_path, stems)
    else:
        out_path = args.out / "applebbch76_instances_all.json"
        convert_to_coco(args.images, args.labels, out_path, stems=None)


if __name__ == "__main__":
    main()