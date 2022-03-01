#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import os
import os.path as path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser, Namespace
from types import SimpleNamespace
from typing import List, Callable

from tqdm import tqdm
from prettytable import PrettyTable

from digitizer.interfaces import Threshold
from digitizer.digitization import annotation_to_thresholds

def compare(report_id, prediction, ground_truth):

    if len(ground_truth) == 0:
        return None

    metrics = {
        "report_id": report_id
    }

    # Get a dataframe of predicted thresholds
    actual_thresholds_df = pd.DataFrame(ground_truth)
    predicted_thresholds_df = pd.DataFrame(prediction)
    metrics["num_predicted_thresholds"] = len(predicted_thresholds_df)

    # Convert to sets
    if len(predicted_thresholds_df) > 0:
        predicted_thresholds = set([tuple(x) for x in predicted_thresholds_df[["ear", "conduction", "masking", "frequency", "threshold"]].values])
    else:
        predicted_thresholds = set([])
    if len(actual_thresholds_df) > 0:
        actual_thresholds = set([tuple(x) for x in actual_thresholds_df[["ear", "conduction", "masking", "frequency", "threshold"]].values])
    else:
        actual_thresholds = set([])

    # Sensitivity
    metrics["actual_thresholds"] = len(actual_thresholds_df)
    metrics["correctly_detected_thresholds"] = sum([1 for t in actual_thresholds if t in predicted_thresholds])
    metrics["missed_thresholds"] = metrics["actual_thresholds"] - metrics["correctly_detected_thresholds"]
    metrics["threshold_sensitivity"] = metrics["correctly_detected_thresholds"]/len(actual_thresholds) if len(actual_thresholds) != 0 else 0

    # Precision
    metrics["predicted_thresholds"] = len(predicted_thresholds_df)
    metrics["correctly_predicted_thresholds"] = sum([1 for t in predicted_thresholds if t in actual_thresholds])
    metrics["incorrect_thresholds"] = metrics["predicted_thresholds"] - metrics["correctly_predicted_thresholds"]
    metrics["threshold_precision"] = metrics["correctly_predicted_thresholds"]/len(predicted_thresholds) if len(predicted_thresholds) != 0 else 0

    return metrics

def main(args: Namespace):
    prediction_files = os.listdir(path.join(args.predictions_dir))

    metrics = []
    with tqdm(total=len(prediction_files), leave=False) as pbar:
        for prediction_file in prediction_files:

            if not prediction_file.endswith(".json"):
                continue

            report_name = prediction_file.split(".")[0]
            prediction_filename = os.path.join(args.predictions_dir, prediction_file)
            annotation_filename = os.path.join(args.annotations_dir, prediction_file)

            pbar.set_description(f"{os.path.basename(prediction_file)}")

            # Load the annotation
            annotation = json.loads(open(annotation_filename).read())
            ground_truth = annotation_to_thresholds(annotation)
            prediction = json.load(open(prediction_filename))

            metrics += [compare(report_name, prediction, ground_truth)]

            pbar.update(1)

    results = pd.DataFrame(metrics)
    
    undigitized_reports = results[results.num_predicted_thresholds == 0]
    digitized_reports = results[results.num_predicted_thresholds > 0]

    failure_rate = len(undigitized_reports)/len(results)
    mean_precision = digitized_reports['threshold_precision'].mean()
    mean_sensitivity = digitized_reports['threshold_sensitivity'].mean()
    mean_missed_thresholds = digitized_reports["missed_thresholds"].mean()
    mean_incorrect_thresholds = digitized_reports["incorrect_thresholds"].mean()

    digitized_reports.incorrect_thresholds.hist()
    plt.savefig("evaluation.png")

    table = PrettyTable(["metric", "value"])
    table.add_row(["Test set size", len(results)])
    table.add_row(["Digitization successful (%)", round(100*(1 - failure_rate), 3)])
    table.add_row(["Digitization failed (%)", round(100*failure_rate, 3)])
    table.add_row(["Mean sensitivity (%)", round(100*mean_sensitivity, 3)])
    table.add_row(["Mean precision (%)", round(100*mean_precision, 3)])
    table.add_row(["Average number of missed thresholds", mean_missed_thresholds])
    table.add_row(["Average number of incorrect thresholds", mean_incorrect_thresholds])
    print(table)

if __name__ == "__main__":
    parser = ArgumentParser(description=(
        "Produces a report that evaluates the performance of the digitizer."
    ))
    parser.add_argument("-p", "--predictions_dir", required=True, type=str,
            help="Path to the directory with the digitizer predictions (JSON).")
    parser.add_argument("-a", "--annotations_dir", required=True, type=str,
            help="Path to the directory with the annotations (JSON).")
    args = parser.parse_args()

    main(args)
