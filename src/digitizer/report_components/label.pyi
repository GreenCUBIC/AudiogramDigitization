from typing_extensions import TypedDict

class Threshold(TypedDict):
    """Represents a hearing threshold (measurement).
    """
    frequency: int
    threshold: int
    ear: str
    masking: bool
    conduction: str

class BoundingBox(TypedDict):
    """Represents the dictionary holding the minimum information
    for a bounding box.
    """
    x: int
    y: int
    width: int
    height: int

class LabelDict(TypedDict):
    """Represents the dictionary for a label as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    text: str
    confidence: float

class SymbolDict(TypedDict):
    """Represents the dictionary for a symbol as extracted
    by the Yolo model.
    """
    boundingBox: BoundingBox
    measurementType: str
    confidence: float
