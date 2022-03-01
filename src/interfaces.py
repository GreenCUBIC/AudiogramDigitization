#!/usr/bin/env python3
"""
Copyright (c) 2020, Carleton University Biomedical Informatics Collaboratory

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List, Optional
from typing_extensions import TypedDict

class ThresholdDict(TypedDict):
    """Represents a hearing threshold (measurement).
    """
    frequency: int
    threshold: int
    ear: str
    masking: bool
    conduction: str
    measurementType: str
    response: bool

class BoundingBox(TypedDict):
    """Represents the dictionary holding the minimum information
    for a bounding box.
    """
    x: int
    y: int
    width: int
    height: int

class AudiogramDict(TypedDict):
    """Represents the dictionary for an audiogram as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    confidence: Optional[float]

class LabelDict(TypedDict):
    """Represents the dictionary for a label as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    value: str
    confidence: Optional[float]

class SymbolDict(TypedDict):
    """Represents the dictionary for a symbol as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    measurementType: str
    confidence: Optional[float]

class CornerDict(TypedDict):
    """Represents a corner, as annotated.
    """
    frequency: int
    threshold: int
    position: TypedDict("PositionDict", { "horizontal": str, "vertical": str })
    x: float
    y: float

class AudiogramAnnotationDict(TypedDict):
    """Represents an audiogram as structured within an annotation.
    """
    confidence: Optional[float]
    correctionAngle: Optional[float]
    boundingBox: BoundingBox
    corners: List[CornerDict]
    labels: List[LabelDict]
    symbols: List[SymbolDict]

class ClaimantProfileDict(TypedDict):
    """Profile of the claimant.
    """
    age: int
    exposure: List[dict] # out of scope for me
    thresholds: List[ThresholdDict]

class CalculationsDict(TypedDict):
    """Values calculated for the claim.
    """
    bestEarPta: float
    correctedBestEarPta: float
    worstEarPta: float
    correctedWorstEarPta: float
    bestEarRabinowitzNotchIndex: Optional[float]
    worstEarRabinowitzNotchIndex: Optional[float]

class HearingLossCriteriaDict(TypedDict):
    """Information related to the hearing loss for the claim.
    Includes different calculated values, etc.
    """
    preliminaryDecisionAvailable: bool
    calculations: CalculationsDict
    eligible: bool
    comment: str
    awardPercentage: float
    reviewNeeded: bool

class MeasurementType(TypedDict):
    """Type of measurement.
    """
    conduction: str
    masking: bool

class SettingsDict(TypedDict):
    """Settings used in computing the eligibility.
    """
    left: TypedDict("EarSettings", { 
        "measurementType": TypedDict("MeasurementType", {
            "conduction": str,
            "masking": bool
        }),
        "ptaFrequencies": List[int]
    })
    right: TypedDict("EarSettings", { 
        "measurementType": TypedDict("MeasurementType", {
            "conduction": str,
            "masking": bool
        }),
        "ptaFrequencies": List[int]
    })

class EligibilityDict(TypedDict):
    """Eligibility information.
    """
    claimantProfile: ClaimantProfileDict
    settings: SettingsDict
    hearingLossCriteria: HearingLossCriteriaDict
    exposureCriteria: dict
