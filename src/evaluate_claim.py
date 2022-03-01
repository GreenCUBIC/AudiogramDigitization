#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import os

from analyzer.eligibility_calculation import determine_eligibility
import utils.audiology as Audiology

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=("Runs the eligibility calculator given a claimant profile and settings."))
    parser.add_argument("-i", "--input", type=str, required=True,
            help=("Path to the JSON file containing the claimant profile, an object with the field `thresholds`, a list of ThresholdDict."))
    parser.add_argument("-o", "--output", type=str, required=False,
            help="Path the the output JSON file. If none provided, the output is printed to the console.")
    parser.add_argument("-l", "--left_ear_settings", nargs="*", help="Settings to compute PTA in the left ear. Enter (in any order) the frequencies used as well as `air` OR `bone` and `masked` or `unmasked`. (Default values assumed if not provided are 500, 1000, 2000, 4000, air, unmasked.)")
    parser.add_argument("-r", "--right_ear_settings", nargs="*", help="Settings to compute PTA in the left ear. Enter (in any order) the frequencies used as well as `air` OR `bone` and `masked` or `unmasked`. (Default values assumed if not provided are 500, 1000, 2000, 4000, air, unmasked.)")
    args = parser.parse_args()

    left_ear_settings = [arg.lower() for arg in args.left_ear_settings]
    right_ear_settings = [arg.lower() for arg in args.right_ear_settings]

    claimant_profile = json.load(open(args.input))

    # Create a SettingsDict from the command line arguments
    settings = {
        "left": {
            "measurementType": {
                "masking": True if "masked" in left_ear_settings else False,
                "conduction": "air" if "bone" not in left_ear_settings else "bone",
            },
            "ptaFrequencies": [int(a) for a in args.left_ear_settings if str.isnumeric(a) and int(a) in Audiology.VALID_FREQUENCIES]
        },
        "right": {
            "measurementType": {
                "masking": True if "masked" in right_ear_settings else False,
                "conduction": "air" if "bone" not in right_ear_settings else "bone",
            },
            "ptaFrequencies": [int(a) for a in args.right_ear_settings if str.isnumeric(a) and int(a) in Audiology.VALID_FREQUENCIES]
        },
    }

    # Compute eligibility
    result = determine_eligibility(claimant_profile, settings)
    result_as_string = json.dumps(result, indent=4, separators=(',', ': '))

    if args.output:
        with open(os.path.join(args.output), "w") as ofile:
            ofile.write(result_as_string)
    else:
        print(result_as_string)
