#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List

import numpy as np

from digitizer.report_components.line import Line

def compute_deviation_sum(angle: float, lines: List[Line]) -> float:
    """Given a candidate angle and a list of lines, computes the sum of the
    deviation of these lines from the horizontal or vertical axis.

    Parameters
    ----------
    angle : float
    The candidate angle in degrees.
    lines : List[Line]
    All the lines used in computing the sum of deviation.

    Returns
    -------
    float
    The sum of the deviations from all lines with the vertical or horizontal
    axis.
    """
    residual_angle_sum = 0
    for line in lines:
        if line.get_angle() > -45  and line.get_angle() < 45:
            residual = abs((line.get_angle() - angle))
            residual_angle_sum += residual
        else:
            residual = 90 - abs(line.get_angle() - angle)
            residual_angle_sum += residual
    return abs(residual_angle_sum)

def compute_rotation_angle(perpendicular_lines: List[Line]) -> float:
    """Given a list of lines, returns the angle that must be applied to
    the image so that lines that all lines that intersect another line
    at roughly a right angle (+/- some tolerance) as close to vertical
    or horizontal as possible.

    Parameters
    ----------
    perpendicular_lines : List[Line}
    The lines extracted from the image. These lines are expected to come
    from an isolated audiogram grid.

    tolerance : float
    Two lines intersecting at 90 +/- `tolerance` degrees are considered
    perpendicular.

    Returns
    -------
    float
    The correction angle that must be applied to the image so as to
    make perpendicular lines as close as possible to horizontal or vertical.
    """
    
    # Find the angle that minimizes the sum of distances to the nearest axis
    #angle.
    angle_range = np.arange(-44, 44, step=0.5)
    errors = [
        compute_deviation_sum(angle, perpendicular_lines)
        for angle in angle_range
    ]
    correction_angle = angle_range[np.argmin(errors)]

    return correction_angle

def apply_rotation(point: dict, rotation_angle: float) -> dict:
    new_x = (np.cos(rotation_angle) * point["x"]
                - np.sin(rotation_angle) * -point["y"])
    new_y = (np.sin(rotation_angle) * point["x"]
                + np.cos(rotation_angle) * -point["y"])
    return { **point, "x": new_x, "y": -new_y }


def get_bounding_box_relative_to_original_report(bounding_box, audiogram_coordinates, correction_angle):

    absolute_corrected_coordinates = {
        "x": bounding_box["x"] + audiogram_coordinates["x"],
        "y": bounding_box["y"] + audiogram_coordinates["y"]
    }

    raw_coordinates = apply_rotation(absolute_corrected_coordinates, -correction_angle)
    correction_angle_rad = np.radians(correction_angle)

    side_length = bounding_box["width"] * np.sin(correction_angle_rad) + bounding_box["width"] * np.cos(correction_angle_rad)
    if correction_angle_rad <= 0:
        return {
            "x": absolute_corrected_coordinates["x"] - bounding_box["width"] * np.sin(correction_angle_rad),
            "y": absolute_corrected_coordinates["y"],
            "width": side_length,
            "height": side_length
        }
    else:
        return {
            "x": absolute_corrected_coordinates["x"],
            "y": absolute_corrected_coordinates["y"] - bounding_box["height"] * np.sin(correction_angle_rad),
            "width": side_length,
            "height": side_length
        }
