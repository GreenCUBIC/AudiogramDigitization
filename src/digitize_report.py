#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import json
import os

from tqdm import tqdm

from digitizer.digitization import generate_partial_annotation, extract_thresholds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=("Digitization script "
            "for the conversion of audiology reports to JSON documents."))
    parser.add_argument("-i", "--input", type=str, required=True,
            help=("Path to the audiology report (or directory) to be digitized."))
    parser.add_argument("-o", "--output_dir", type=str, required=False,
            help="Path to the directory in which the result is to be saved (file will have same base name as input file, but with .json extension). If not provided, result is printed to the console.")
    parser.add_argument("-a", "--annotation_mode", action="store_true",
            help="Whether the script should be run in `annotation mode`, i.e. return results similar in format to those of a human-made annotation. If not given, a list of thresholds is computed.")
    parser.add_argument("-g", "--gpu", action="store_true",
            help="Use the GPU.")
    args = parser.parse_args()

    input_files = []
    if os.path.isfile(args.input):
        input_files += [os.path.abspath(args.input)]
    else:
        input_files += [os.path.join(args.input, filename) for filename in os.listdir(args.input)]

    with tqdm(total=len(input_files)) as pbar:
        for input_file in input_files:
            pbar.set_description(f"{os.path.basename(input_file)}")

            result = None

            if args.annotation_mode:
                result = generate_partial_annotation(input_file, gpu=args.gpu)
            else:
                result = extract_thresholds(input_file, gpu=args.gpu)

            result_as_string = json.dumps(result, indent=4, separators=(',', ': '))

            if args.output_dir:
                predictions_filename = os.path.basename(input_file).split(".")[0] + ".json"
                with open(os.path.join(args.output_dir, predictions_filename), "w") as ofile:
                    ofile.write(result_as_string)
            else:
                print(result_as_string)

            pbar.update(1) # increment the progress bar
