#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List

import PIL.ImageDraw
import numpy as np

class Line(object):

    def __init__(self, x1, y1, x2, y2, color="rgb(255,0,0)", label=None):
        self.p1 = { "x": x1, "y": y1 }
        self.p2 = { "x": x2, "y": y2 }
        self.color = color
        self.label = label

    def get_angle(self) -> float:
        """Returns the angle of the line in degrees in the range [0, 180[.

        Returns
        -------
        float
        The angle of the line in degrees.
        """
        dx = self.p2["x"] - self.p1["x"]
        dy = self.p2["y"] - self.p1["y"]
        angle = np.degrees(np.arctan2(abs(dy), abs(dx)))
        if self.p2["y"] - self.p1["y"] < 0:
            angle = 180 - angle
        return angle


    def has_a_perpendicular_line(self, lines: List["Line"], tolerance: float = 1) -> bool:
        """Checks if a line has at least one perpendicular line among a list
        of lines.

        Parameters
        ----------
        lines : List[Line]
        A list of lines.

        tolerance : float
        A difference of `tolerance` from a 90 degrees angle between the two lines
        is still considered perpendicular.

        Returns
        -------
        bool
        `True` if the line has a perpendicular line in the list, `False` otherwise.

        """
        assert tolerance >= 0

        line_angle1 = self.get_angle()
        for other_line in lines:
            line_angle2 = other_line.get_angle()
            angle = abs(line_angle1 - line_angle2)
            if abs(angle - 90) < tolerance:
                return True
        return False

    def get_x(self) -> int:
        """Return the middle x pixel coordinate of a vertical line.

        Only applicable to vertical lines.

        Returns
        -------
        int
        The middle x coordinate of a vertical line.
        """
        assert self.is_vertical() 
        return int((self.p1["x"] + self.p2["x"]) / 2)

    def get_y(self) -> int:
        """Return the middle y pixel coordinate of a horizontal line.

        Only applicable to horizontal lines.

        Returns
        -------
        int
        The middle y coordinate of a horizontal line.
        """
        assert self.is_horizontal() 
        return (self.p1["y"] + self.p2["y"]) / 2

    def is_vertical(self, tolerance: float = 1) -> bool:
        """Returns true if the line is vertical.

        Parameters
        ----------
        tolerance : float
        A deviation of `tolerance` degrees from the vertical line is still
        considered vertical.

        Returns
        -------
        bool
        True if the line is vertical, False otherwise.
        """
        assert tolerance >= 0

        angle = self.get_angle()
        return angle <= (-90 + tolerance) or angle >= (90 - tolerance)

    def is_horizontal(self, tolerance: float = 1) -> bool:
        """Returns true if the line is horizontal.

        Parameters
        ----------
        tolerance : float
        A deviation of `tolerance` degrees from the horizontal line is still
        considered horizontal.

        Returns
        -------
        bool
        True if the line is horiontal, False otherwise.
        """
        assert tolerance >= 0

        angle = self.get_angle()
        return angle >= -tolerance and angle <= tolerance

    def crosses_label(self, labels: List["Label"]) -> bool:
        """Checks if the line intersects one of the labels passed.

        Parameters
        ----------
        labels : List[Label]
        A list of labels that the line could possibly cross.

        Returns
        -------
        bool
        True if the line crosses at least one Label among the ones provided,
        False otherwise.
        """
        for label in labels:
            if self.is_vertical():
                x = (self.p1["x"] + self.p2["x"]) / 2
                if x >= label.p1["x"] and x <= label.p2["x"]:
                    return True
            elif self.is_horizontal():
                y = (self.p1["y"] + self.p2["y"]) / 2
                if y >= label.p1["y"] and y <= label.p2["y"]:
                    return True
        return False


    def draw(self, canvas: PIL.ImageDraw):
        """Draws the line on the canvas (image) passed.

        Parameters
        ----------
        canvas : PIL.ImageDraw
        The PIL.ImageDraw on which the line is to be displayed.
        """

        canvas.line([
            (self.p1["x"], self.p1["y"]),
            (self.p2["x"], self.p2["y"])
        ], width=3, fill=self.color)

        if self.label:
            canvas.text((self.p1["x"] + 5, self.p1["y"]), str(self.label), fill=self.color)
