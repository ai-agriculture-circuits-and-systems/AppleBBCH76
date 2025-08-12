from __future__ import annotations

"""Generate train/val/test split lists for AppleBBCH76.

This script is used to generate the train/val/test splits for the AppleBBCH76 dataset, producing
`sets/train.txt`, `sets/val.txt`, `sets/test.txt`, and `sets/all.txt` with one
image id (stem without extension) per line.

Usage:
    python scripts/generate_splits.py --images data/images --out sets \
        --train 0.8 --val 0.1 --test 0.1 --seed 42
"""

import argparse
import random
from pathlib import Path
from typing import List, Sequence, Tuple


def _collect_image_stems(images_dir: Path) -> List[str]:
    """Return sorted list of image stems from a directory.

    Args:
        images_dir: Directory containing image files.

    Returns:
        Sorted list of basenames without extension for files with .jpg.
    """

    stems = [p.stem for p in images_dir.glob("*.jpg")]
    return sorted(stems)


def _split_stems(
    stems: Sequence[str], train_ratio: float, val_ratio: float, test_ratio: float, seed: int
) -> Tuple[List[str], List[str], List[str]]:
    """Split stems into train/val/test.

    Args:
        stems: All image ids.
        train_ratio: Fraction for train set.
        val_ratio: Fraction for val set.
        test_ratio: Fraction for test set.
        seed: RNG seed for reproducibility.

    Returns:
        (train, val, test) lists of stems.
    """

    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-6:
        raise ValueError("train+val+test ratios must sum to 1.0")

    rng = random.Random(seed)
    shuffled = list(stems)
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_train = int(round(n * train_ratio))
    n_val = int(round(n * val_ratio))
    train = shuffled[:n_train]
    val = shuffled[n_train : n_train + n_val]
    test = shuffled[n_train + n_val :]
    return train, val, test


def _write_list(path: Path, rows: Sequence[str]) -> None:
    """Write a newline-separated list to a file, creating parent dirs."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    """CLI to generate split files for AppleBBCH76."""

    parser = argparse.ArgumentParser(description="Generate train/val/test splits")
    parser.add_argument("--images", type=Path, default=Path("data/images"))
    parser.add_argument("--out", type=Path, default=Path("sets"))
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--val", type=float, default=0.1)
    parser.add_argument("--test", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    stems = _collect_image_stems(args.images)
    train, val, test = _split_stems(stems, args.train, args.val, args.test, args.seed)

    _write_list(args.out / "train.txt", train)
    _write_list(args.out / "val.txt", val)
    _write_list(args.out / "test.txt", test)
    _write_list(args.out / "train_val.txt", train + val)
    _write_list(args.out / "all.txt", stems)

    print(
        f"Wrote {len(train)} train, {len(val)} val, {len(test)} test (total {len(stems)}) to {args.out}"
    )


if __name__ == "__main__":
    main()


