#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import pathlib
import json
import os
import subprocess as sp
import tempfile
from typing import List, Callable

from tqdm import tqdm
import numpy as np

from interfaces import AudiogramDict, AudiogramAnnotationDict, ThresholdDict
from digitizer.report_components.grid import Grid
from digitizer.report_components.label import Label
from digitizer.report_components.symbol import Symbol
from digitizer.report_components.report import Report
import utils.audiology as Audiology
from utils.geometry import compute_rotation_angle, apply_rotation

DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "..") # current directory

def detect_audiograms(filepath: str, weights: str, device: str = "cpu") -> List[AudiogramDict]:
    """Runs the audiogram detector.

    The detector is run as a subprocess.

    Parameters
    ----------
    filepath : str
    Path to the image on which the detector is to be run.
    weights : str
    Path to the file holding the weights of the neural network (detector).
    device : str
    "cpu" or "gpu"

    Returns
    -------
    List[AudiogramDict]
    The AudiogramDict corresponding to the audiograms detected in the report.
    """
    subprocess = sp.Popen([
        "python3",
        f"{os.path.join(DIR, 'digitizer/yolov5/detect_audiograms.py')}",
        "--source", f"{filepath}",
        "--weights", weights,
        "--device", device
    ], stdout=sp.PIPE) # TODO timeout should be an environment variable
    output = subprocess.stdout.read().decode("utf-8")
    audiograms = json.loads(output.split("$$$")[1])
    return audiograms

def detect_labels(filepath: str, weights: str, audiogram_coordinates: dict, correction_angle: float, device: str = "cpu") -> List[Label]:
    """Runs the label detector.

    The detector is run as a subprocess.

    Parameters
    ----------
    filepath : str
    Path to the image on which the detector is to be run.
    audiogram_coordinates: dict
    The coordinates of the audiogram { "x": int, "y": int } needed to convert the label locations 
    with respect to the top-left corner of the bounding audiogram to relative to the top-left corner
    of the report.
    correction_angle: float
    The correction angle in degrees that was applied to the audiogram, so that it can be reversed to
    get the coordinates of the label with respect to the top-left corner of the original unrotated report.
    weights : str
    Path to the file holding the weights of the neural network (detector).
    device : str
    "cpu" or "gpu"

    Returns
    -------
    List[Label]
    A list of Label objects (NOT LabelDict).
    """
    subprocess = sp.Popen([
        "python3",
        os.path.join(DIR, "digitizer/yolov5/detect_labels.py"),
        "--source", f"{filepath}",
        "--weights", weights,
        "--device", device
    ], stdout=sp.PIPE)
    output = subprocess.stdout.read().decode("utf-8")
    parsed = json.loads(output.split("$$$")[1])
    label_dicts = parsed
    labels = [Label(label, audiogram_coordinates, correction_angle) for label in parsed]
    return labels

def detect_symbols(filepath: str, weights: str, audiogram_coordinates: dict, correction_angle: float, device: str = "cpu") -> List[Symbol]:
    """Runs the symbol detector.

    The detector is run as a subprocess.

    Parameters
    ----------
    filepath : str
    Path to the image on which the detector is to be run.
    audiogram_coordinates: dict
    The coordinates of the audiogram { "x": int, "y": int } needed to convert the label locations 
    with respect to the top-left corner of the bounding audiogram to relative to the top-left corner
    of the report.
    correction_angle: float
    The correction angle in degrees that was applied to the audiogram, so that it can be reversed to
    get the coordinates of the label with respect to the top-left corner of the original unrotated report.
    weights : str
    Path to the file holding the weights of the neural network (detector).
    device : str
    "cpu" or "gpu"

    Returns
    -------
    List[Label]
    A list of Symbol objects (NOT SymbolDict).
    """
    subprocess = sp.Popen([
        "python3",
        os.path.join(DIR, "digitizer/yolov5/detect_symbols.py"),
        "--source", filepath,
        "--weights", weights,
        "--device", device
    ], stdout=sp.PIPE)

    output = json.loads(subprocess.stdout.read().decode("utf-8").split("$$$")[1])
    symbols = [Symbol(detection, audiogram_coordinates, correction_angle) for detection in output]
    return symbols

def detect_components(filepath: str, gpu: bool = False) -> List:
    """Invokes the object detectors.

    Parameters
    ----------
    filepath : str
    Path to the image.
    gpu : bool
    Whether the GPU should be used (default: False).
    
    Returns
    -------
    List
    A list (of length 0, 1 or 2) of the form 
    [
      { "audiogram": AudiogramDict, "labels": List[Label], "symbols": List[Symbol] }, # plot 1
      { "audiogram": AudiogramDict, "labels": List[Label], "symbols": List[Symbol] } # plot 2
    ]
    """

    components = []

    # Detect audiograms within the report
    audiogram_model_weights_path = os.path.join(DIR, "..", "models/audiograms/latest/weights/best.pt")
    audiograms = detect_audiograms(f"{filepath}", audiogram_model_weights_path)

    # If no audiogram is detected, return...
    if len(audiograms) == 0:
        return components

    # Iterate through every audiogram in the report
    for i, audiogram in enumerate(audiograms):
        components.append({})

        # Load the report
        report = Report(filename=filepath)

        # Generate a cropped version of the report around the detected audiogram
        report = report.crop(
            audiogram["boundingBox"]["x"],
            audiogram["boundingBox"]["y"],
            audiogram["boundingBox"]["x"] + audiogram["boundingBox"]["width"],
            audiogram["boundingBox"]["y"] + audiogram["boundingBox"]["height"]
        )

        # Create a temporary file
        cropped_file = tempfile.NamedTemporaryFile(suffix=".jpg")

        # Correct for rotation
        lines = report.detect_lines(threshold=200)
        perpendicular_lines = [
            line for line in lines
            if line.has_a_perpendicular_line(lines)
            and (abs(line.get_angle() - 90) < 10
            or  abs(line.get_angle()) < 10)
        ]
        correction_angle = compute_rotation_angle(perpendicular_lines)
        audiogram["correctionAngle"] = correction_angle
        report = report.rotate(correction_angle)
        report.save(cropped_file.name)

        audiogram_coordinates = {
            "x": audiogram["boundingBox"]["x"],
            "y": audiogram["boundingBox"]["y"]
        }

        components[i]["audiogram"] = audiogram

        labels_model_weights_path = os.path.join(DIR, "..", "models/labels/latest/weights/best.pt")
        components[i]["labels"] = detect_labels(cropped_file.name, labels_model_weights_path, audiogram_coordinates, correction_angle)
        symbols_model_weights_path = os.path.join(DIR, "..", "models/symbols/latest/weights/best.pt")
        components[i]["symbols"] = detect_symbols(cropped_file.name, symbols_model_weights_path, audiogram_coordinates, correction_angle)

    return components

def generate_partial_annotation(filepath: str, gpu: bool = False) -> List[AudiogramAnnotationDict]:
    """Generates a seed annotation to be completed in the nihl portal.

    It is ``partial`` because it does not locate the corners of the audiogram.

    Parameters
    ----------
    filepath : str
    Path to the file for which an initial annotation is to b
    gpu : bool
    Whether the gpu should be used.

    Returns
    -------
    List[AudiogramAnnotationDict]
    An Annotation dict.
    """
    components = detect_components(filepath, gpu=gpu)
    audiograms = []
    for i in range(len(components)):
        audiogram = components[i]["audiogram"]
        audiogram["labels"] = [label.to_dict() for label in components[i]["labels"]]
        audiogram["symbols"] = [symbol.to_dict() for symbol in components[i]["symbols"]]
        audiogram["corners"] = [] # these are not located by the algorithm
        audiograms.append(audiogram)
    return audiograms

def extract_thresholds(filepath: str, gpu: bool = False) -> List[ThresholdDict]:
    """Extracts the thresholds from the report.

    parameters
    ----------
    filepath : str
    Path to the file for which an initial annotation is to b
    gpu : bool
    Whether the gpu should be used.

    Returns
    -------
    list[ThresholdDict]
    A list of thresholds.
    """
    components = detect_components(filepath, gpu=gpu)

    thresholds = []

    # For each audiogram, extract the thresholds and append them to the
    # thresholds list
    for i in range(len(components)):
        audiogram = components[i]["audiogram"]
        labels = components[i]["labels"]
        symbols = components[i]["symbols"]

        report = Report(filename=filepath)
        report = report.crop(
            audiogram["boundingBox"]["x"],
            audiogram["boundingBox"]["y"],
            audiogram["boundingBox"]["x"] + audiogram["boundingBox"]["width"],
            audiogram["boundingBox"]["y"] + audiogram["boundingBox"]["height"]
        )
        report = report.rotate(audiogram["correctionAngle"])

        try:
            grid = Grid(report, labels)
        except Exception as e:
            continue

        thresholds += [{
            "ear": symbol.ear,
            "conduction": symbol.conduction,
            "masking": symbol.masking,
            "measurementType": Audiology.stringify_measurement(symbol.to_dict()),
            "frequency": grid.get_snapped_frequency(symbol),
            "threshold": grid.get_snapped_threshold(symbol),
            "response": True # IMPORTANT: assume that a response was obtain for measurements
            }
            for symbol in symbols
        ]
    return thresholds

def get_correction_angle(corners: List[dict]) -> float:
    """Computes the rotation angle that must be applied based on
    corner coordinates to get an unrotated audiogram.

    Parameters
    ----------
    corners : List[dict]
    A list of corners.

    Returns
    -------
    float
    The rotation angle that must be applied to correct for the rotation
    of the audiogram.
    """
    # sort the corners
    corners = sorted(corners, key=lambda c: c["y"])
    top_corners = sorted(corners[2:], key=lambda c: c["x"])
    bottom_corners = sorted(corners[0:2], key=lambda c: c["x"])

    # Find the rotation angle based on the top_corners 2 corners
    dx1 = top_corners[1]["x"] - top_corners[0]["x"]
    dy1 = top_corners[1]["y"] - top_corners[0]["y"]
    angle1 = np.arcsin(abs(dy1)/abs(dx1))

    # Repeat for the bottom_corners angles
    dx2 = bottom_corners[1]["x"] - bottom_corners[0]["x"]
    dy2 = bottom_corners[1]["y"] - bottom_corners[0]["y"]
    angle2 = np.arcsin(abs(dy2)/abs(dx2))

    return np.sign(dy1) * np.mean([angle1, angle2])

def get_conversion_maps(corners: List[dict]) -> List[Callable]:
    """Computes the functions that map pixel coordinates to frequency-threshold coordinates
    and vice versa.

    Parameters
    ----------
    corners : List[dict]
    The audiogram corners.

    Returns
    -------
    List[Callable]
    A list of lambda functions. These functions all accept a single float argument.
    They are in the following order.
    1. pixel->frequency
    2. pixel->threshold
    3. frequency->pixel
    4. threshold->pixel
    """

    # For x axis
    y_sorted_corners = sorted(corners, key=lambda c: c["y"])
    top_corners = sorted(y_sorted_corners[0:2], key=lambda c: c["x"])
    o_max = Audiology.frequency_to_octave(top_corners[1]["frequency"]) # max octave
    x_max = top_corners[1]["x"] # max pixel value
    o_min = Audiology.frequency_to_octave(top_corners[0]["frequency"]) # min octave
    x_min = top_corners[0]["x"]
    frequency_map = lambda p: Audiology.octave_to_frequency(o_min + (o_max - o_min)*(p - x_min)/(x_max - x_min))
    inverse_frequency_map = lambda f: x_min + (Audiology.frequency_to_octave(f) - o_min)*(x_max - x_min)/(o_max - o_min)

    # For y axis
    x_sorted_corners = sorted(corners, key=lambda c: c["x"])
    left_corners = sorted(x_sorted_corners[0:2], key=lambda c: c["y"])
    t_max = left_corners[1]["threshold"] # max threshold
    y_max = left_corners[1]["y"] # max pixel value
    t_min = left_corners[0]["threshold"]
    y_min = left_corners[0]["y"]
    threshold_map = lambda p: t_min + (t_max - t_min)*(p - y_min)/(y_max - y_min)
    inverse_threshold_map = lambda t: y_min + (t - t_min)*(y_max - y_min)/(t_max - t_min)

    return [frequency_map, threshold_map, inverse_frequency_map, inverse_threshold_map]

def annotation_to_thresholds(audiograms: dict) -> List[ThresholdDict]:
    """Extracts the thresholds from an annotation.

    Parameters
    ----------
    audiograms : dict
    An annotation.

    Returns
    -------
    List[ThresholdDict]
    A list of thresholds
    """
    combined_thresholds = []
    for audiogram in audiograms:
        correction_angle = get_correction_angle(audiogram["corners"])
        corners = [apply_rotation(corner, correction_angle) for corner in audiogram["corners"]]
        frequency_map, threshold_map, inverse_frequency_map, inverse_threshold_map = get_conversion_maps(corners)

        thresholds: List[ThresholdDict] = []
        for symbol in audiogram["symbols"]:
            symbol_center = {
                "x": symbol["boundingBox"]["x"] + symbol["boundingBox"]["width"] / 2,
                "y": symbol["boundingBox"]["y"] + symbol["boundingBox"]["height"] / 2,
            }
            symbol = { **symbol, "boundingBox": symbol_center }
            new_symbol = {**symbol, "boundingBox": apply_rotation(symbol["boundingBox"], correction_angle) }
            bounding_box = new_symbol["boundingBox"]
            ear = "left" if "left" in new_symbol["measurementType"].lower() else "right"
            conduction = "air" if "air" in new_symbol["measurementType"].lower() else "bone"
            masking = False if "unmasked" in new_symbol["measurementType"].lower() else True
            if conduction == "air":
                frequency = Audiology.round_frequency(frequency_map(bounding_box["x"]))
            else:
                frequency = Audiology.round_frequency_bone(frequency_map(bounding_box["x"]), ear)
            threshold = Audiology.round_threshold(threshold_map(bounding_box["y"]))

            thresholds.append({
                "ear": ear,
                "conduction": conduction,
                "masking": masking,
                "frequency": frequency,
                "threshold":  threshold,
                "response": True, # IMPORTANT: assume that a response was measured for threshold
                "measurementType": f"{conduction}_{'MASKED' if masking else 'UNMASKED'}_{ear}".upper()
            })

        combined_thresholds += thresholds

    return combined_thresholds
