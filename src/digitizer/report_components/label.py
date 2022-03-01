#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
from typing import List, Optional, Type
import PIL.ImageDraw
import numpy as np

from interfaces import LabelDict
from utils.geometry import get_bounding_box_relative_to_original_report
import utils.audiology as Audiology

class Label(object):

    def __init__(self, label_dict: dict, audiogram_coordinates: dict, correction_angle: float):
        bbox = label_dict["boundingBox"]
        self.p1 = { 
            "x": bbox["x"],
            "y": bbox["y"]
        }

        self.p2 = { 
            "x": bbox["x"] + bbox["width"],
            "y": bbox["y"] + bbox["height"]
        }

        self.dimensions = { 
            "width": bbox["width"],
            "height": bbox["height"]
        }

        self.text = label_dict["text"]

        self.absolute_bounding_box = get_bounding_box_relative_to_original_report(bbox, audiogram_coordinates, correction_angle)

    def draw(self, canvas: PIL.ImageDraw):
        """Draws the label on the canvas (image) passed.

        Parameters
        ----------
        canvas : PIL.ImageDraw
        The PIL.ImageDraw on which the labels are to be displayed.
        """
        color = "rgb(255,0,0)" if self.is_frequency() else "rgb(0,0,255)"
        canvas.rectangle(
            (self.p1["x"], self.p1["y"], self.p2["x"], self.p2["y"]),
            outline=color,
            width=3
        )
        canvas.text((self.p1["x"], self.p1["y"] - 10), str(self.get_value()), fill=color)

    def get_type(self) -> str:
        """Returns the type of label.

        Returns
        -------
        str
        The type of label (`threshold` or `frequency`).
        """

        if self.is_frequency():
            return "frequency"
        elif self.is_threshold():
            return "threshold"
        else:
            return None

    def get_value(self) -> int:
        """Returns the numerical value of the label.

        Returns
        -------
        int
        The numerical value of the label (in dB if threshold, or in Hz if frequency). 
        """
        if not self.is_frequency() and not self.is_threshold():
            raise "Attempted to get the value of a label which is not a frequency or threshold."

        raw_value = float(self.text.lower()\
                .rstrip("hz")\
                .rstrip("h")\
                .rstrip("khz")\
                .rstrip("k"))

        # If the value extracted is < 100 and corresponds to one of the
        # standard frequency values, the value is in kHz, which we can
        # convert to Hz.
        if self.is_frequency() and raw_value < 100:
            return raw_value * 1000

        return raw_value


    def is_frequency(self) -> bool:
        """Checks if the label corresponds to a frequency.

        Returns
        -------
        bool
        True if the label corresponds to a frequency, False otherwise.
        """
        if not isinstance(self.text, str):
            return False

        try:
            stripped_label = self.text.lower()\
                    .rstrip("hz")\
                    .rstrip("h")\
                    .rstrip("khz")\
                    .rstrip("k")
            frequency_label = float(stripped_label)
            return frequency_label in Audiology.OCTAVE_FREQS_HZ \
                    or frequency_label in Audiology.OCTAVE_FREQS_KHZ
        except ValueError:
            return False # label cannot be converted to a float

    def is_threshold(self) -> bool:
        """Checks if the label corresponds to a threshold.

        Returns
        -------
        bool
        True if the label corresponds to a threshold, False otherwise.
        """
        try:
            value = int(self.text)
            return value in list(range(-10, 130, 10))
        except ValueError:
            return False

    def get_area(self) -> int:
        """Computes the area of the label's bounding box.

        Returns
        -------
        int
        The area of the label's bounding box in pixels squared.
        """
        return self.dimensions["height"] * self.dimensions["width"]

    def overlaps_vertically_with(self, label: "Label") -> bool:
        """Checks of the label overlaps vertically with the label passed.

        Returns
        -------
        bool
        True if the labels overlap and False otherwise.
        """
        return (self.p1["y"] >= label.p1["y"] and self.p1["y"] <= label.p2["y"]) \
                or (self.p2["y"] >= label.p1["y"] and self.p2["y"] <= label.p2["y"]) \
                or (label.p1["y"] >= self.p1["y"] and label.p1["y"] <= self.p2["y"]) \
                or (label.p2["y"] >= self.p1["y"] and label.p2["y"] <= self.p2["y"])

    def overlaps_horizontally_with(self, label: "Label") -> bool:
        """Checks of the label overlaps horizontally with the label passed.

        Returns
        -------
        bool
        True if the labels overlap and False otherwise.
        """
        return (self.p1["x"] >= label.p1["x"] and self.p1["x"] <= label.p2["x"]) \
                or (self.p2["x"] >= label.p1["x"] and self.p2["x"] <= label.p2["x"]) \
                or (label.p1["x"] >= self.p1["x"] and label.p1["x"] <= self.p2["x"]) \
                or (label.p2["x"] >= self.p1["x"] and label.p2["x"] <= self.p2["x"])

    def overlaps_with(self, label: "Label") -> bool:
        """Checks of the label overlaps vertically OR horizontally with the label passed.

        Returns
        -------
        bool
        True if the labels overlap and False otherwise.
        """
        return self.overlaps_vertically_with(label) and self.overlaps_horizontally_with(label)

    def encompasses_x_value(self, x: int) -> bool:
        """Checks of the the pixel value of x pass is encompassed in the label's x range.

        Returns
        -------
        bool
        True if x is in the label's x range and False otherwise.
        """
        return x >= self.p1["x"] and x <= self.p2["x"]

    def encompasses_y_value(self, y: int) -> bool:
        """Checks of the the pixel value of y pass is encompassed in the label's y range.

        Returns
        -------
        bool
        True if y is in the label's y range and False otherwise.
        """
        return y >= self.p1["y"] and y <= self.p2["y"]

    def get_center(self) -> dict:
        """Returns the center of the label's bounding box.

        Returns
        -------
        dict
        A dictionary describing the center of the label's bounding box
        of the form { "x": int, "y": int }.
        """
        center = {
            "x": int((self.p1["x"] + self.p2["x"]) / 2),
            "y": int((self.p1["y"] + self.p2["y"]) / 2)
        }
        return center
        

    def find_closest_line(self, lines: List["Line"]) -> "Line":
        """Find the closest line to the label.

        If the label corresponds to a frequency, the line is vertical,
        otherwise it is a horizontal line.

        Parameters
        ----------
        lines : List[Line]
        The set of lines detected in the audiogram image.

        Returns
        -------
        Line
        The closest line.
        """
        if self.is_threshold():
            lines = [line for line in lines if line.is_horizontal()]
            closest_line_distance = 100000
            closest_line_index = None
            distances = []
            for i, line in enumerate(lines):
                distance = abs(line.get_y() - self.get_center()["y"])
                distances.append(distance)
                if distance < closest_line_distance:
                    closest_line_index = i
                    closest_line_distance = distance
            return lines[closest_line_index], distances[closest_line_index]

        elif self.is_frequency():
            lines = [line for line in lines if line.is_vertical()]
            closest_line_distance = 100000
            closest_line_index = None
            distances = []
            for i, line in enumerate(lines):
                distance = abs(line.get_x() - self.get_center()["x"])
                distances.append(distance)
                if distance < closest_line_distance:
                    closest_line_index = i
                    closest_line_distance = distance
            return lines[closest_line_index], distances[closest_line_index]
        else:
            raise "Error: Tried to find the closest line to a label that corresponds neither to a frequency nor a threshold."

    def to_dict(self) -> dict:
        """Returns the label as a dictionary.

        More thorough description of the function here.

        Returns
        -------
        dict
        The label as a dictionary with the keys `boundingBox` and `value`.

        """
        return {
            "boundingBox": self.absolute_bounding_box,
            "value": self.text
        }


    def __str__(self):
        return f"Textbox(x={self.p1['x']}, y={self.p1['y']}, text={self.text})"

    def __repr__(self):
        return self.__str__()
