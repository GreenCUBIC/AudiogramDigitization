import argparse
import os.path as osp
import os

import pandas as pd


def main(args):

    n_audiograms = len(os.listdir(args.input_dir))
    unable_to_digitize = 0
    for prediction_file in os.listdir(args.input_dir):
        predictions = pd.read_csv(osp.join(args.input_dir, prediction_file))
        ground_truth = pd.read_csv(osp.join(args.ground_truth_dir, prediction_file))

        predictions_dicts = predictions.to_dict(orient="records")
        ground_truth_dicts = ground_truth.to_dict(orient="records")

        if len(predictions_dicts) == 0:
            unable_to_digitize += 1
            continue

        correct_identification = []
        incorrect_identification = []
        for threshold in predictions_dicts:
            if threshold in ground_truth_dicts:
                correct_identification.append(threshold)
            else:
                incorrect_identification.append(threshold)

        correct_detection = []
        incorrect_detection = []
        for threshold in ground_truth_dicts:
            if threshold in predictions_dicts:
                correct_detection.append(threshold)
            else:
                incorrect_detection.append(threshold)
        
        
        precision = len(correct_identification) / len(predictions_dicts)
        recall = len(correct_detection) / len(ground_truth_dicts)
        print(f"RECALL = {recall} PRECISION = {precision}")

    print(f"Unable to digitize {unable_to_digitize}/{n_audiograms} audiograms...")
                


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True, help="Path to the directory with the predictions.")
    parser.add_argument("-g", "--ground_truth_dir", required=True, help="Path to the directory with the ground truth annotations.")
    args = parser.parse_args()
    
    main(args)