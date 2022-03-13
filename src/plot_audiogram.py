from argparse import ArgumentParser
import json

import matplotlib.pyplot as plt
import pandas as pd

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

    # y axis
    ax.set_ylim(-11, 120)
    ax.invert_yaxis()
    ax.set_ylabel('Threshold (dB HL)')

    plt.grid()

    for conduction in ("air", "bone"):
        for masking in (True, False):
            for ear in ("left", "right"):
                selection = thresholds[(thresholds.conduction == conduction) & (thresholds.ear == ear) & (thresholds.masking == masking)]

                ax.scatter(selection.frequency, selection.threshold)


    plt.show()



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the JSON file of the digitized audiogram.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Where the output file should be saved.")
    args = parser.parse_args()
    main(args)