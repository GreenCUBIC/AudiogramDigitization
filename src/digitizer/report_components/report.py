#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
from typing import Optional, List
import os

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

from .label import Label
from .line import Line
from .grid import Grid

class Report(object):

    def __init__(self, filename: Optional[str] = None, image: Optional[Image.Image] = None):
        assert not (filename and image) and bool(filename) != bool(image)
        if filename:
            self.filename = filename
            self.pil_image = Image.open(filename)
        else:
            self.filename = None
            self.pil_image = image

    def rescale(self, factor: float) -> "Report":
        """Creates a new Report that has been resized.

        Parameters
        ----------
        factor : float
        The resize factor.

        Returns
        -------
        Report
        A new Report that has be rescaled.
        """
        return Report(image=self.pil_image.resize(int(self.pil_image.width * factor), int(self.pil_image.height * factor)))

    def rotate(self, angle: float) -> "Report":
        """Creates a new Report that has been rotated.

        Parameters
        ----------
        angle : float
        The rotation (in degrees) to apply (CCW).

        Returns
        -------
        Report
        A new Report that has be rotated.
        """
        return Report(image=self.pil_image.rotate(angle, center=(0,0), fillcolor="rgb(255,255,255)"))

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> "Report":
        """Creates a new cropped Report.

        Parameters
        ----------
        x1: int
        The x pixel coordinate of the top-left corner.
        y1: int
        The y pixel coordinate of the top-left corner.
        x2: int
        The x pixel coordinate of the bottom-right corner.
        y2: int
        The y pixel coordinate of the bottom-right corner.

        Returns
        -------
        Report
        A new cropped Report.
        """
        return Report(image=self.pil_image.crop((x1, y1, x2, y2)))

    def show(
        self,
        labels: Optional[List[Label]] = [],
        lines:  Optional[List[Line]] = [],
        grids: Optional[List[Grid]] = [],
        points: Optional[List[tuple]] = [],
        title: Optional[str] = None,
        filename: Optional[str] = None
    ):
        """Displays the audiogram on the screen, and saves it to a file
        if `filename` parameter is provided.

        Parameters
        ----------
        labels : List[Label]
        A list of labels to show (default: []).
        lines : List[Lines]
        A list of lines to show (default: []).
        grids : List[Grid]
        A list of grids to show (default: []).
        points : List[dict]
        A list of points of the form { "x": int, "y": int } to show (default: []).
        title: str
        The title of the plot
        filename: Optional[str]
        The path to where the image should be save. Image is not saved
        if no filename is provided (default: None).
        """
        labeled_copy = self.pil_image.copy().convert("RGB")
        drawing = ImageDraw.Draw(labeled_copy)
        fontpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets", "fonts", "Arial.ttf")
        font = None
        try:
            font = ImageFont.truetype(fontpath, 32)
        except:
            font = ImageFont.truetype("DejaVuSans.ttf", 32)

        for label in labels:
            label.draw(drawing)

        for line in lines:
            line.draw(drawing)

        for grid in grids:
            grid.draw(drawing)

        for point in points:
            r = 5 # radius
            drawing.ellipse([(point[0] - r, point[1] - r), (point[0] + r, point[1] + r)], fill="rgb(0,0,255)")

        if title:
            drawing.text((self.pil_image.size[0]/2, 50), title, font=font, align="center", fill="rgb(53,155,232)")

        if filename:
            labeled_copy.save(filename)

        labeled_copy.show()

    def save(
        self,
        filename: str,
        labels: Optional[List[Label]] = [],
        lines:  Optional[List[Line]] = [],
        grids: Optional[List[Grid]] = [],
        title: Optional[str] = None,
    ):
        """Saves the report to a file along with annotations for the
        provided report elements.

        Parameters
        ----------
        filename: str
        The path to where the image should be save.
        labels : List[Label]
        A list of labels to show (default: []).
        lines : List[Lines]
        A list of lines to show (default: []).
        grids : List[Grid]
        A list of grids to show (default: []).
        title: str
        The title of the plot
        """
        labeled_copy = self.pil_image.copy().convert("RGB")
        drawing = ImageDraw.Draw(labeled_copy)
        fontpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets", "Arial.ttf")
        font = None
        try:
            font = ImageFont.truetype(fontpath, 32)
        except:
            font = ImageFont.truetype("DejaVuSans.ttf", 32)


        for label in labels:
            label.draw(drawing)

        for line in lines:
            line.draw(drawing)

        for grid in grids:
            grid.draw(drawing)

        if title:
            drawing.text((self.pil_image.size[0]/2, 50), title, font=font, align="center", fill="rgb(53,155,232)")

        labeled_copy.save(filename)

    def get_image(self, resize_factor: float = 1) -> Image:
        """Returns a copy of the PIL image representing the report.

        Parameters
        ----------
        resize_factor : float
        The resize factor of the image sought (default: 1).

        Returns
        -------
        PIL.Image
        A copy of the image at the resize factor provided.
        """

        return self.pil_image.resize(
            (int(self.pil_image.size[0] * resize_factor),
             int(self.pil_image.size[1] * resize_factor))
        )

    def detect_lines(self, threshold=250) -> List[Line]:
        """Detects lines in the report using the Hough Transform.

        For details, see: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html

        Parameters
        ----------
        threshold : int
        The threshold above which a line is detected. See documentation for OpenCV's HoughLine function for details.

        Returns
        -------
        List[Line]
        A list of lines detected in the report.
        """
        gray = np.array(self.get_image())
        edges = cv2.Canny(gray, 150, 300, apertureSize = 3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold, None, 0, 0)

        if lines is None:
            return []

        lines_list = []

        for line in lines:
            for l in (line[0],):
                rho = l[0]
                theta = l[1]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                lines_list.append(Line(x1, y1, x2, y2))

        return lines_list
