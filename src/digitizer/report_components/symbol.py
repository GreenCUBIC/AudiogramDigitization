#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List, Optional, Type
import PIL.ImageDraw

from interfaces import SymbolDict
from .line import Line
from .label import Label
import utils.audiology as Audiology
from utils.geometry import get_bounding_box_relative_to_original_report

class Symbol(object):

    def __init__(self, symbol_dict: dict, audiogram_coordinates: dict, correction_angle: float):
        bbox = symbol_dict["boundingBox"]
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

        self.absolute_bounding_box = get_bounding_box_relative_to_original_report(bbox, audiogram_coordinates, correction_angle)

        self.ear = "left" if "left" in symbol_dict["measurementType"].lower() else "right"
        self.masking = False if "unmasked" in symbol_dict["measurementType"].lower() else True
        self.conduction = "air" if "air" in symbol_dict["measurementType"].lower() else "bone"
        self.measurement_type = symbol_dict["measurementType"]
        self.confidence = symbol_dict["confidence"]

    def draw(self, canvas: PIL.ImageDraw):
        """Draws the symbol's bounding box on the canvas (image) passed.

        Parameters
        ----------
        canvas : PIL.ImageDraw
        The PIL.ImageDraw on which the symbol is to be displayed.
        """
        color = "rgb(255,0,0)" if self.is_frequency() else "rgb(0,0,255)"
        canvas.rectangle(
            (self.p1["x"], self.p1["y"], self.p2["x"], self.p2["y"]),
            outline=color,
            width=3
        )
        canvas.text((self.p1["x"], self.p1["y"] - 10), str(self.get_value()), fill=color)

    def get_center(self):
        """Returns the center of the symbol's bounding box.

        Returns
        -------
        dict
        A dictionary describing the center of the symbol's bounding box
        of the form { "x": int, "y": int }.
        """
        center = {
            "x": (self.p1["x"] + self.p2["x"]) / 2,
            "y": (self.p1["y"] + self.p2["y"]) / 2
        }
        return center

    def to_dict(self) -> dict:
        """Serializes the symbol to a dictionary.

        Returns
        -------
        dict
        A dictionary representing the symbol.
        """
        return {
            "boundingBox": self.absolute_bounding_box,
            "ear": self.ear,
            "conduction": self.conduction,
            "masking": self.masking,
            "confidence": self.confidence,
            "response": True,
            "measurementType": self.measurement_type
        }
        
    def __str__(self):
        return f"Threshold(ear={self.ear}, conduction={self.conduction})"

    def __repr__(self):
        return self.__str__()
