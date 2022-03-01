#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List
from PIL import ImageDraw
from digitizer.report_components.line import Line
from digitizer.report_components.label import Label
from digitizer.report_components.symbol import Symbol
import utils.audiology as Audiology
from utils.exceptions import InsufficientLinesException

class Grid(object):

    def __init__(self, report, labels, threshold=150):
        lines = report.detect_lines(threshold=threshold)
        lines = [line for line in lines if line.is_vertical() or line.is_horizontal()]
        frequency_labels = [label for label in labels if label.is_frequency()]
        threshold_labels = [label for label in labels if label.is_threshold()]

        if len(lines) == 0 or \
            all([line.is_vertical() for line in lines]) \
            or all([line.is_horizontal() for line in lines]):
            raise InsufficientLinesException()

        x_lines = [label.find_closest_line(lines) for label in frequency_labels]
        x_pixels = [line[0].get_x() for line in x_lines]
        x_frequency = [label.get_value() for label in frequency_labels]
        self.x_distances = [line[1] for line in x_lines]

        y_lines = [label.find_closest_line(lines) for label in threshold_labels]
        y_pixels = [line[0].get_y() for line in y_lines]
        y_threshold = [label.get_value() for label in threshold_labels]
        self.y_distances = [line[1] for line in y_lines]

        x_points = sorted(list(zip(x_pixels, x_frequency)), key=lambda p: p[0])
        y_points = sorted(list(zip(y_pixels, y_threshold)), key=lambda p: p[0])

        # Take the first and last points for the octaves (frequencies)
        o_max = Audiology.frequency_to_octave(x_points[-1][1]) # max octave
        x_max = x_points[-1][0] # max pixel value
        o_min = Audiology.frequency_to_octave(x_points[0][1])
        x_min = x_points[0][0]

        # Take the first and last points for the thresholds
        t_max = y_points[-1][1] # max threshold
        y_max = y_points[-1][0] # max pixel value
        t_min = y_points[0][1]
        y_min = y_points[0][0]

        if x_min == x_max or y_max == y_min:
            raise InsufficientLinesException()

        # Derive the forward and reverse mapping functions via simple linear
        # interpolation using the **OCTAVE SCALE** (which is linear), because
        # the frequency scale is logarithmic.
        self.pixel_freq_map = lambda p: Audiology.octave_to_frequency(o_min + (o_max - o_min)*(p - x_min)/(x_max - x_min))
        self.freq_pixel_map = lambda f: x_min + (Audiology.frequency_to_octave(f) - o_min)*(x_max - x_min)/(o_max - o_min)

        # Linear interpolation can be applied directly to the thresholds,
        # because the threshold axis is linear.
        self.pixel_threshold_map = lambda p: t_min + (t_max - t_min)*(p - y_min)/(y_max - y_min)
        self.threshold_pixel_map = lambda t: y_min + (t - t_min)*(y_max - y_min)/(t_max - t_min)

    def get_x(self, frequency: float) -> int:
        """Given a frequency value, returns the x coordinate predicted by the
        grid.

        Parameters
        ----------
        frequency : float
        The frequency value whose x-position on the image is to be determined.

        Returns
        -------
        int
        The x position (in pixels) of the frequency, as predicted by the grid.
        """
        return self.freq_pixel_map(frequency)

    def get_frequency(self, symbol: Symbol) -> float:
        """Returns the frequency of the symbol.

        Parameters
        ----------
        symbol : Symbol
        The symbol whose frequency is to be extracted using the computed grid.

        Returns
        -------
        float
        The frequency value (in Hz).
        """
        return self.pixel_freq_map(symbol.get_center()["x"])


    def get_snapped_frequency(self, symbol: Symbol, epsilon: float = 0.15) -> float:
        """Returns the frequency of the symbol, snapped to the nearest
        commonly recorded frequency (all octaves and select semi-octaves).

        Parameters
        ----------
        symbol : Symbol
        The symbol whose frequency is to be extracted using the computed grid.

        epsilon: float
        Distance (in octaves) below which the bone threshold is snapped to
        the nearest frequency as opposed to shifted to the nearest threshold
        in the direction of the corresponding ear.

        Returns
        -------
        int
        The `snapped-to-the-grid` frequency value (in Hz).
        """
        if symbol.conduction == "air":
            return Audiology.round_frequency(self.pixel_freq_map(symbol.get_center()["x"]))
        else:
            return Audiology.round_frequency_bone(self.pixel_freq_map(symbol.get_center()["x"]), symbol.ear, epsilon=epsilon)


    def get_y(self, threshold: float) -> int:
        """Given a threshold value, returns the y coordinate predicted by the
        grid.

        Parameters
        ----------
        threshold : float
        The threshold value whose y-position on the image is to be determined.

        Returns
        -------
        int
        The y position (in pixels) of the threshold, as predicted by the grid.
        """
        return self.threshold_pixel_map(threshold)


    def get_threshold(self, symbol: Symbol) -> int:
        """Returns the threshold of the symbol.

        Parameters
        ----------
        symbol : Symbol
        The symbol whose threshold is to be extracted using the computed grid.

        Returns
        -------
        int
        The  threshold value.
        """
        return self.pixel_threshold_map(symbol.get_center()["y"])


    def get_snapped_threshold(self, symbol: Symbol) -> int:
        """Returns the threshold of the symbol, snapped to the nearest 5dB.

        Parameters
        ----------
        symbol : Symbol
        The symbol whose threshold is to be extracted using the computed grid.

        Returns
        -------
        int
        The `snapped-to-the-grid` threshold value.
        """
        return Audiology.round_threshold(self.pixel_threshold_map(symbol.get_center()["y"]))

    def draw(
        self,
        image_drawer: ImageDraw,
        frequency_range: List[int] = [125, 8000],
        threshold_range:  List[int] = [-10, 120],
        color: str = "rgb(255,0,0)"
    ):
        """Draws the calculated grid on the provided image.

        Parameters
        ----------
        image : PIL.ImageDraw
        The `ImageDraw` object with which the grid is to be drawn.

        frequency_range : [int, int]
        The minimum and maximum value of the frequencies to be included
        (default: [250, 8000]).

        threshold_range : [int, int]
        The minimum and maximum value of the threshold to be included
        (default: [-10, 120]).

        color: str
        Color of the grid as a string of the form =`rgb(R,G,B)`.
        """
        lines = []
        for freq in Audiology.OCTAVE_FREQS_HZ:
            x = self.get_x(freq)
            y1 = self.get_y(threshold_range[0])
            y2 = self.get_y(threshold_range[1])
            line = Line(x, y1, x, y2, color=color, label=freq)
            line.draw(image_drawer)

        for threshold in Audiology.THRESHOLDS:
            x1 = self.get_x(frequency_range[0])
            x2 = self.get_x(frequency_range[1])
            y = self.get_y(threshold)
            line = Line(x1, y, x2, y, color=color, label=threshold)
            line.draw(image_drawer)
