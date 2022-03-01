#!/usr/bin/env python3
"""
Copyright (c) 2020 Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
from typing import List
from types import SimpleNamespace
import argparse, os, json, shutil
from tqdm import tqdm
import os.path as path
import numpy as np
from PIL import Image

LABEL_CLASS_INDICES = {
    "250": 0,
    ".25": 1,
    "500": 2,
    ".5": 3,
    "1000": 4,
    "1": 5,
    "1K": 6,
    "2000": 7,
    "2": 8,
    "2K": 9,
    "4000": 10,
    "4": 11,
    "4K": 12,
    "8000": 13,
    "8": 14,
    "8K": 15,
    "0": 16,
    "20": 17,
    "40": 18,
    "60": 19,
    "80": 20,
    "100": 21,
    "120": 22
}

def extract_labels(annotation: dict, image: Image) -> List[tuple]:
    """Extracts the bounding boxes of labels into a tuple compatible
    the YOLOv5 format.

    Parameters
    ----------
    annotation : dict
    A dictionary containing the annotations for the audiograms in a report.

    image : Image
    The image in PIL format corresponding to the annotation.

    Returns
    -------
    tuple
    A tuple of the form
    (class index, x_center, y_center, width, height) where all coordinates
    and dimensions are normalized to the width/height of the image.
    """
    label_label_tuples = []
    image_width, image_height = image.size
    for audiogram in annotation:
        for label in audiogram["labels"]:
            bounding_box = label["boundingBox"]
            x_center = (bounding_box["x"] + bounding_box["width"] / 2) / image_width
            y_center = (bounding_box["y"] + bounding_box["height"] / 2) / image_height
            box_width = bounding_box["width"] / image_width
            box_height = bounding_box["height"] / image_width
            try:
                label_label_tuples.append((LABEL_CLASS_INDICES[label["value"]], x_center, y_center, box_width, box_height))
            except:
                continue
    return label_label_tuples

def create_directory_structure(data_dir: str):
    try:
        shutil.rmtree(path.join(data_dir))
    except:
        pass
    os.mkdir(path.join(data_dir))
    os.mkdir(path.join(data_dir, "images"))
    os.mkdir(path.join(data_dir, "images", "train"))
    os.mkdir(path.join(data_dir, "images", "validation"))
    os.mkdir(path.join(data_dir, "labels"))
    os.mkdir(path.join(data_dir, "labels", "train"))
    os.mkdir(path.join(data_dir, "labels", "validation"))

def create_yolov5_file(bboxes: List[tuple], filename: str):
    # Turn the bounding boxes into a string with a bounding box
    # on each line
    file_content = "\n".join([
        f"{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} {bbox[4]}"
        for bbox in bboxes
    ])

    # Save to a file
    with open(filename, "w") as output_file:
        output_file.write(file_content)

def all_labels_valid(labels: List[tuple]):
    for label in labels:
        for value in label[1:]:
            if value < 0 or value > 1:
                return False
    return True


def main(args: SimpleNamespace):

    # Find all the JSON files in the input directory
    report_ids = [
        filename.rstrip(".json")
        for filename in os.listdir(path.join(args.annotations_dir))
        if filename.endswith(".json")
        and path.exists(path.join(args.images_dir, filename.rstrip(".json") + ".jpg"))
    ]

    # Shuffle
    np.random.seed(seed=42) # for reproducibility of the shuffle
    np.random.shuffle(report_ids)

    # Create the directory structure in which the images and annotations
    # are to be stored
    create_directory_structure(args.data_dir)

    # Iterate through the report ids, extract the annotations in YOLOv5 format
    # and place the file in the correct directory, and the image in the correct
    # directory.
    for i, report_id in enumerate(tqdm(report_ids)):

        # Decide if the image is going into the training set or validation set
        directory = (
            "train" if i < args.train_frac * len(report_ids) else "validation"
        )

        # Load the annotation`
        annotation_content = open(
            path.join(args.annotations_dir, f"{report_id}.json")
        )

        image = Image.open(os.path.join(args.images_dir, f"{report_id}.jpg"))

        annotation = json.load(annotation_content)
        bounding_boxes = extract_labels(annotation, image)

        if not all_labels_valid(bounding_boxes):
            continue

        # Open the corresponding image to get its dimensions
        image = Image.open(os.path.join(args.images_dir, f"{report_id}.jpg"))

        create_yolov5_file(
            bounding_boxes,
            path.join(args.data_dir, "labels", directory, f"{report_id}.txt")
        )
        image.save(
            path.join(args.data_dir, "images", directory, f"{report_id}.jpg")
        )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=(
        "Script that formats the training set for transfer learning of labels detection via "
        "the YOLOv5 model."
    ))
    parser.add_argument("-d", "--data_dir", type=str, required=True, help=(
        "Path to the directory where the training set should be created."
    ))
    parser.add_argument("-a", "--annotations_dir", type=str, required=True, help=(
        "Path to the directory containing the annotations in the JSON format." 
    ))
    parser.add_argument("-i", "--images_dir", type=str, required=True, help=(
        "Path to the directory containing the images." 
    ))
    parser.add_argument("-f", "--train_frac", type=float, required=True, help=(
        "Fraction of images to be used for training. (e.g. 0.8)"
    ))
    args = parser.parse_args()

    main(args)

