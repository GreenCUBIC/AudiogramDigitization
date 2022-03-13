#!/usr/bin/env python3
"""
Copyright (c) 2022, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
from argparse import ArgumentParser
import json

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
import pandas as pd

def load_image(path, zoom=1):
    return OffsetImage(plt.imread(path), zoom=zoom)

def main(args):

    thresholds = pd.DataFrame(json.load(open(args.input)))

    # Figure
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # x axis
    axis = [250, 500, 1000, 2000, 4000, 8000, 16000]
    ax.set_xscale('log')
    ax.xaxis.tick_top()
    ax.xaxis.set_major_formatter(plt.FuncFormatter('{:.0f}'.format))
    ax.set_xlabel('Frequency (Hz)')
    ax.xaxis.set_label_position('top') 
    ax.set_xlim(125,16000)
    plt.xticks(axis)

    # y axis
    ax.set_ylim(-20, 120)
    ax.invert_yaxis()
    ax.set_ylabel('Threshold (dB HL)')

    plt.grid()

    for conduction in ("air", "bone"):
        for masking in (True, False):
            for ear in ("left", "right"):
                symbol_name = f"{ear}_{conduction}_{'unmasked' if not masking else 'masked'}"
                selection = thresholds[(thresholds.conduction == conduction) & (thresholds.ear == ear) & (thresholds.masking == masking)]
                selection = selection.sort_values("frequency")

                # Plot the symbols
                for i, threshold in selection.iterrows():
                    ab = AnnotationBbox(load_image(f"src/digitizer/assets/symbols/{symbol_name}.png", zoom=0.1), (threshold.frequency, threshold.threshold), frameon=False)
                    ax.add_artist(ab)

                # Add joining line for air conduction thresholds
                if conduction == "air":
                    plt.plot(selection.frequency, selection.threshold, color="red" if ear == "right" else "blue", linewidth=0.5)

    # Save audiogram plot to PNG
    output = args.output
    if not output.endswith(".png"):
        output = output.split(".")[0] + ".png"

    plt.savefig(output)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the JSON file of the digitized audiogram.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Where the output file should be saved.")
    args = parser.parse_args()
    main(args)