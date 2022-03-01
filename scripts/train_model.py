#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import subprocess as sp
import datetime
from types import SimpleNamespace

def main(args: SimpleNamespace):

    log_dir = f"model_{datetime.datetime.now().isoformat()}"

    models = []

    if args.audiograms_model: models.append("audiograms")
    if args.labels_model: models.append("labels")
    if args.symbols_model: models.append("symbols")

    if len(models) == 0:
        print("No model to train... see instructions with `-h`.")
        return

    for model in models:
        print(f"Training the {model} detection model...")

        # Format the dataset
        print("Formatting the dataset...")
        returncode = sp.call([(
            f"python3 models/{model}/format_dataset.py \\"
            f"-a {args.training_data}/annotations \\"
            f"-i {args.training_data}/images \\"
            f"-d models/{model}/dataset \\"
            f"-f 0.8")
        ], shell=True)
        if returncode != 0:
            return

        # Train the model
        print("Training the model...")
        returncode = sp.call([("python src/digitizer/yolov5/train.py \\"
            f"--img-size 1024 \\"
            f"--rect \\"
            f"--batch 16 \\"
            f"--epochs 100 \\"
            f"--data models/{model}/{model}_detection.yaml \\"
            f"--cfg models/{model}/yolov5s.yaml \\"
            f"--hyp models/{model}/latest/hyp.yaml \\"
            f"--weights src/digitizer/yolov5/weights/yolov5s.pt \\"
            f"--logdir models/{model}/{log_dir} \\"
            f"--device {0 if args.gpu else 'cpu'}\\")
        ], shell=True)
        if returncode != 0: return

        # Move the new training data
        print("Saving the model data...")
        sp.call([f"rm -rf models/{model}/latest"], shell=True)
        sp.call([f"cp -r models/{model}/{log_dir} models/{model}/latest"], shell=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Trains the detection model(s) using the provided training data.")
    parser.add_argument("-t", "--training_data", required=True, type=str,
                        help="Path to the directory containing the training data. Should contain the subdirectories `images` and `annotations`.")
    parser.add_argument("-s", "--symbols_model", action="store_true",
                        help="Pass this flag if the symbol detection model should be trained.")
    parser.add_argument("-l", "--labels_model", action="store_true",
                        help="Pass this flag if the labels detection model should be trained.")
    parser.add_argument("-a", "--audiograms_model", action="store_true",
                        help="Pass this flag if the audiogram detection model should be trained.")
    parser.add_argument("-g", "--gpu", action="store_true",
                        help="Pass this flag to use a GPU for training.")
    args = parser.parse_args()

    main(args)
