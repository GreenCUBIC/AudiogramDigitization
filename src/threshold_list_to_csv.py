#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import argparse
import json
import os

from digitizer.digitization import annotation_to_thresholds

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True, help="Path to directory with predictions in JSON format (thresholds list).")
    parser.add_argument("-o", "--output_dir", required=True, help="Path to directory where the CSVs should be dumped.")
    args = parser.parse_args()

    for filename in os.listdir(args.input_dir):
        thresholds = json.load(open(f"{args.input_dir}/{filename}"))
        thresholds_list = []
        for threshold in thresholds:
            thresholds_list.append([threshold["ear"], threshold["conduction"], threshold["masking"], threshold["frequency"], threshold["threshold"]])
        
        with open(f"{args.output_dir}/{filename.split('.')[0]}.csv", "w") as ofile:
            ofile.write(f"ear,conduction,masking,frequency,threshold\n")
            for t in thresholds_list:
                ofile.write(f"{t[0]},{t[1]},{t[2]},{t[3]},{t[4]}\n")