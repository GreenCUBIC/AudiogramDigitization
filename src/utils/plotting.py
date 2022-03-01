#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
from typing import List
import os.path as path
import io

import PIL.Image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib

from interfaces import Threshold

# Path to the folder containing the symbols that get plotted
SYMBOLS_DIR = path.join(path.dirname(__file__), "..", "assets", "symbols")

def figure_to_image(figure: matplotlib.pyplot.figure, size, dpi=300):
    """Converts a matplotlib figure to a PIL Image.

    Parameters
    ----------
    figure : matplotlib.pyplot.figure
    The figure to convert to an image.

    size: tuple
    Dimensions of the image in pixels.

    dpi: int
    Resolution (default: 300)

    Returns
    -------
    PIL.Image
    The image of the plot in PIL format.
    """
    # Save the figure to a buffer
    image_buffer = io.BytesIO()
    figure.set_size_inches((size[0]/dpi, size[1]/dpi))
    figure.savefig(image_buffer, dpi=dpi)

    # Open image from buffer
    image_buffer.seek(0)
    image = PIL.Image.open(image_buffer)

    return image

def plot_audiogram(thresholds: List[Threshold]) -> plt.figure:
    """Given a list of threshold dictionaries, plots the audiogram.

    Parameters
    ----------
    thresholds : List[Threshold]
    A list of dictionaries that implement the `Threshold` interface.

    Returns
    -------
    matplotlib.pyplot.figure
    The `Figure` object corresponding to the audiogram.
    """
    # Plot setup
    fig = plt.figure()
    ax = plt.gca()

    # Setup axes
    plt.xscale("log")
    ax.set_xlim(125, 8000) # Standard audios go from 125 to 8000 Hz 
    ax.set_ylim(-20, 120) # Most go from -10 to 120, but let's start at -20, in case
    plt.gca().invert_yaxis()

    # Add the ticks
    ax.set_xticks([125, 250, 500, 1000, 2000, 4000, 8000]) # Octave frequencies
    ax.set_yticks(list(range(-20, 120, 10))) # All multiples of 10
    ax.get_xaxis().set_major_formatter(
        matplotlib.ticker.FormatStrFormatter("%.0f")
    )

    # Show the grid
    plt.grid()

    # Iterate through the different symbols
    for ear in ("left", "right"):
        for masking in (True, False):
            for conduction in ("air", "bone"):
                # Filter out all other symbols to generate an individual curve
                curve = [
                    threshold 
                    for threshold
                    in thresholds 
                    if threshold["ear"] == ear
                    and threshold["masking"] == masking
                    and threshold["conduction"] == conduction
                ]

                # Sort the thresholds on the curve in order of frequency
                curve = sorted(curve, key=lambda t: t["frequency"])
                freq = [t["frequency"] for t in curve]
                threshold = [t["threshold"] for t in curve]

                # For every threshold (freq, thresh) belonging to the curve
                # considered in this loop iteration, add a symbol on the plot.
                for (f, t) in zip(freq, threshold):
                    icon_name = f"{ear}_{conduction}_{'masked' if masking else 'unmasked'}.png"
                    icon_img = plt.imread(path.join(SYMBOLS_DIR, icon_name))
                    icon = AnnotationBbox(
                                OffsetImage(icon_img, zoom=0.1), 
                                (f, t),
                                frameon=False
                            )
                    ax.add_artist(icon)

    return fig
